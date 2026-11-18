"""Gemini (free tier) se baat karne wali file. Koi bhi error app ko crash nahi karta."""
import json
import os
import urllib.error
import urllib.request

from . import config

BASE = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"
# Pehla model chalay to theek, warna agla try hota hai. GEMINI_MODEL secret se badal sakte hain.
MODELS = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"]

SYSTEM_PROMPT = """You are MediMind AI, a friendly health-information assistant.
Rules:
- Reply in the same language/script the user writes in (English, Urdu script, or Roman Urdu).
- Keep answers short, simple and patient-friendly. Explain medical terms in plain words.
- You are NOT a doctor. Never give a definitive diagnosis, never prescribe, never tell the
  user to start/stop a medicine or change a dose.
- Ask at most 1-2 relevant follow-up questions (onset, severity, duration) when needed.
- Say clearly when you are unsure. Never invent facts or references.
- If symptoms could be serious, advise seeing a doctor; for life-threatening signs tell the
  user to call local emergency services (Pakistan: Rescue 1122) immediately.
- End health answers with a short reminder to consult a licensed doctor."""


def _models():
    custom = os.getenv("GEMINI_MODEL", "").strip()
    return ([custom] if custom else []) + MODELS


def _call(model, payload, key):
    req = urllib.request.Request(
        BASE.format(model),
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def chat(history, patient_context=""):
    """history: [{'role':'user'|'assistant','content':str}, ...]
    Returns (text, None) ya (None, error_message)."""
    key = config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    if not key:
        return None, "AI key set nahi hai. Streamlit Secrets mein GEMINI_API_KEY check karein."
    system = SYSTEM_PROMPT
    if patient_context:
        system += "\n\nPatient context (shared with consent):\n" + patient_context
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [
            {"role": "user" if m["role"] == "user" else "model",
             "parts": [{"text": m["content"]}]}
            for m in history
        ],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1024},
    }
    last_err = "AI se jawab nahi mila."
    for model in _models():
        try:
            data = _call(model, payload, key)
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(p.get("text", "") for p in parts).strip()
            if text:
                return text, None
            last_err = "AI ne khali jawab diya. Dobara try karein."
        except urllib.error.HTTPError as e:
            if e.code in (400, 401, 403):
                return None, "API key ghalat ya block lag rahi hai. Key dobara check karein."
            if e.code == 429:
                last_err = "Free limit khatam ho gayi hai. Thori der baad try karein."
            elif e.code == 404:
                last_err = "Model nahi mila."
            else:
                last_err = f"AI service ka masla (code {e.code})."
        except (urllib.error.URLError, TimeoutError):
            last_err = "Internet ya AI service se rabta nahi ho saka."
        except (KeyError, IndexError, ValueError):
            last_err = "AI ka jawab samajh nahi aaya."
    return None, last_err
