import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import load_dotenv

# Always load this workspace's .env and allow overriding stale shell variables.
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

FEATHERLESS_BASE_URL = os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1")
FEATHERLESS_PERSONALIZER_MODEL = os.getenv("FEATHERLESS_PERSONALIZER_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")
FEATHERLESS_FINAL_MODEL = os.getenv("FEATHERLESS_FINAL_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")
FEATHERLESS_AGENT_MODEL = os.getenv("FEATHERLESS_AGENT_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")


def _first_non_empty_env(*keys):
    for key in keys:
        value = os.getenv(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _featherless_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "CouncilAgent/1.0 (+https://local.app)"
    }


def _call_featherless_completion(prompt, model, api_key, temperature=0.7):
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature
    }

    request_url = f"{FEATHERLESS_BASE_URL.rstrip('/')}/completions"
    request = urllib.request.Request(
        request_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=_featherless_headers(api_key),
        method="POST"
    )

    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read().decode("utf-8")
                body = json.loads(raw)
                choices = body.get("choices", []) if isinstance(body, dict) else []
                if not choices:
                    return f"[ERROR]: Featherless completion response missing choices - {raw[:300]}"

                first = choices[0] if isinstance(choices[0], dict) else {}
                content = first.get("text", "") if isinstance(first, dict) else ""
                if not isinstance(content, str) or not content.strip():
                    return f"[ERROR]: Featherless completion response missing text - {raw[:300]}"

                return content.strip()
        except urllib.error.URLError as e:
            if "timed out" in str(e).lower() and attempt == 0:
                continue
            raise


def _call_featherless_chat(prompt, model, api_key, temperature=0.7):
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }

    request_url = f"{FEATHERLESS_BASE_URL.rstrip('/')}/chat/completions"
    request = urllib.request.Request(
        request_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=_featherless_headers(api_key),
        method="POST"
    )

    try:
        raw = ""
        for attempt in range(2):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    raw = response.read().decode("utf-8")
                    break
            except urllib.error.URLError as e:
                if "timed out" in str(e).lower() and attempt == 0:
                    continue
                raise

        body = json.loads(raw)
        choices = body.get("choices", []) if isinstance(body, dict) else []
        if not choices:
            return f"[ERROR]: Featherless response missing choices - {raw[:300]}"

        message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
        content = message.get("content", "") if isinstance(message, dict) else ""
        if not isinstance(content, str) or not content.strip():
            return f"[ERROR]: Featherless response missing message content - {raw[:300]}"

        return content.strip()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        lowered = error_body.lower()

        # Some base models (e.g., gemma-2-27b) may not expose a chat template.
        # Retry automatically on the raw completions endpoint.
        if "chat template" in lowered and "transformers v4.44" in lowered:
            try:
                return _call_featherless_completion(prompt, model, api_key, temperature=temperature)
            except urllib.error.HTTPError as completion_err:
                completion_body = completion_err.read().decode("utf-8", errors="ignore")
                return f"[ERROR]: Featherless completion HTTP {completion_err.code} - {completion_body}"
            except Exception as completion_error:
                return f"[ERROR]: Featherless completion fallback failed - {str(completion_error)}"

        if "error code: 1010" in lowered:
            return (
                "[ERROR]: Featherless HTTP 403 (Cloudflare 1010 access denied). "
                "This is an edge/WAF block, not agent logic failure. "
                "Check FEATHERLESS_BASE_URL, key validity, network/VPN/proxy, and retry from a different network."
            )
        return f"[ERROR]: Featherless HTTP {e.code} - {error_body}"
    except Exception as e:
        return f"[ERROR]: {str(e)}"

def call_llm(prompt):
    """Call Featherless API for council agent generations."""
    api_key = _first_non_empty_env("FEATHERLESS_API_KEY", "FEATHERLESS_FINAL_API_KEY")
    if not api_key:
        return "[ERROR]: FEATHERLESS_API_KEY or FEATHERLESS_FINAL_API_KEY is not set."

    return _call_featherless_chat(
        prompt=prompt,
        model=FEATHERLESS_AGENT_MODEL,
        api_key=api_key,
        temperature=0.7
    )


def call_personalizer_llm(prompt, temperature=0.7):
    """Call Featherless API for personalizer-specific generations."""
    api_key = _first_non_empty_env("FEATHERLESS_API_KEY", "FEATHERLESS_FINAL_API_KEY")
    if not api_key:
        return "[ERROR]: FEATHERLESS_API_KEY or FEATHERLESS_FINAL_API_KEY is not set."

    return _call_featherless_chat(
        prompt=prompt,
        model=FEATHERLESS_PERSONALIZER_MODEL,
        api_key=api_key,
        temperature=temperature
    )


def call_personalizer_final_llm(prompt, temperature=0.7):
    """Call Featherless API for final personalized answer generation."""
    api_key = _first_non_empty_env("FEATHERLESS_FINAL_API_KEY", "FEATHERLESS_API_KEY")
    if not api_key:
        return "[ERROR]: FEATHERLESS_FINAL_API_KEY or FEATHERLESS_API_KEY is not set."

    return _call_featherless_chat(
        prompt=prompt,
        model=FEATHERLESS_FINAL_MODEL,
        api_key=api_key,
        temperature=temperature
    )