import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import load_dotenv

# Always load this workspace's .env to get API key.
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

# Groq configuration constants (non-secret configuration)
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_AGENT_MODEL = "llama-3.1-8b-instant"
GROQ_PERSONALIZER_MODEL = "llama-3.1-8b-instant"
GROQ_FINAL_MODEL = "llama-3.1-8b-instant"
GROQ_FALLBACK_MODEL = "llama-3.1-8b-instant"


def _first_non_empty_env(*keys):
    for key in keys:
        value = os.getenv(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _groq_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "BattleOfBots/1.0 (+https://local.app)"
    }


def _call_groq_chat(prompt, model, api_key, temperature=0.7):
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
    }

    request_url = f"{GROQ_BASE_URL.rstrip('/')}/chat/completions"
    request = urllib.request.Request(
        request_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=_groq_headers(api_key),
        method="POST",
    )

    try:
        for attempt in range(2):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    raw = response.read().decode("utf-8")
                    break
            except urllib.error.URLError as e:
                if "timed out" in str(e).lower() and attempt == 0:
                    continue
                raise
        else:
            return "[ERROR]: Groq request timed out after retries."

        body = json.loads(raw)
        choices = body.get("choices", []) if isinstance(body, dict) else []
        if not choices:
            return f"[ERROR]: Groq response missing choices - {raw[:300]}"

        message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
        content = message.get("content", "") if isinstance(message, dict) else ""
        if not isinstance(content, str) or not content.strip():
            return f"[ERROR]: Groq response missing message content - {raw[:300]}"

        return content.strip()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        lowered = error_body.lower()

        if e.code == 429 and model != GROQ_FALLBACK_MODEL:
            return _call_groq_chat(
                prompt=prompt,
                model=GROQ_FALLBACK_MODEL,
                api_key=api_key,
                temperature=temperature,
            )

        if e.code == 404 and "model" in lowered and model != GROQ_FALLBACK_MODEL:
            return _call_groq_chat(
                prompt=prompt,
                model=GROQ_FALLBACK_MODEL,
                api_key=api_key,
                temperature=temperature,
            )

        if "error 1010" in lowered or "cloudflare" in lowered:
            return (
                "[ERROR]: Groq request blocked by Cloudflare 1010 (access denied). "
                "Use a different network/VPN setting, verify account access, or regenerate a key from Groq console."
            )

        return f"[ERROR]: Groq HTTP {e.code} - {error_body}"
    except Exception as e:
        return f"[ERROR]: {str(e)}"


def call_llm(prompt):
    """Call Groq API for agent generations."""
    api_key = _first_non_empty_env("GROQ_API_KEY")
    if not api_key:
        return "[ERROR]: GROQ_API_KEY is not set."

    return _call_groq_chat(
        prompt=prompt,
        model=GROQ_AGENT_MODEL,
        api_key=api_key,
        temperature=0.7,
    )


def call_personalizer_llm(prompt, temperature=0.7):
    """Call Groq API for question/personalizer generations."""
    api_key = _first_non_empty_env("GROQ_API_KEY")
    if not api_key:
        return "[ERROR]: GROQ_API_KEY is not set."

    return _call_groq_chat(
        prompt=prompt,
        model=GROQ_PERSONALIZER_MODEL,
        api_key=api_key,
        temperature=temperature,
    )


def call_personalizer_final_llm(prompt, temperature=0.7):
    """Call Groq API for final evaluation generations."""
    api_key = _first_non_empty_env("GROQ_API_KEY")
    if not api_key:
        return "[ERROR]: GROQ_API_KEY is not set."

    return _call_groq_chat(
        prompt=prompt,
        model=GROQ_FINAL_MODEL,
        api_key=api_key,
        temperature=temperature,
    )