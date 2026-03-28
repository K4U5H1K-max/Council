from groq import Groq
import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import load_dotenv

# Always load this workspace's .env and allow overriding stale shell variables.
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

FEATHERLESS_BASE_URL = os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1")
FEATHERLESS_PERSONALIZER_MODEL = "meta-llama/Meta-Llama-3-8B"
FEATHERLESS_FINAL_MODEL = "deepseek-ai/DeepSeek-V3-0324"
FEATHERLESS_AGENT_MODEL = os.getenv("FEATHERLESS_AGENT_MODEL", "meta-llama/Meta-Llama-3-8B")


def _first_non_empty_env(*keys):
    for key in keys:
        value = os.getenv(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


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
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
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
        return f"[ERROR]: Featherless HTTP {e.code} - {error_body}"
    except Exception as e:
        return f"[ERROR]: {str(e)}"

def call_llm(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        error_text = str(e).lower()
        if "rate limit" in error_text or "429" in error_text:
            featherless_key = _first_non_empty_env("FEATHERLESS_API_KEY", "FEATHERLESS_FINAL_API_KEY")
            if featherless_key:
                fallback_response = _call_featherless_chat(
                    prompt=prompt,
                    model=FEATHERLESS_AGENT_MODEL,
                    api_key=featherless_key,
                    temperature=0.7
                )
                if "[ERROR]" not in fallback_response:
                    return fallback_response

        return f"[ERROR]: {str(e)}"


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