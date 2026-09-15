from __future__ import annotations

import os
import traceback
from pathlib import Path

from dotenv import load_dotenv

from src.intents import guess_language, local_reply
from src.languages import SOUTH_AFRICAN_LANGUAGES

_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_ENV, override=True)

DEAD_CHAT_MODELS = {
    "llama-3.1-8b-instant": "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile": "openai/gpt-oss-120b",
}


def _api_key() -> str:
    load_dotenv(_ENV, override=True)
    raw = (
        os.getenv("OPENAI_API_KEY", "").strip()
        or os.getenv("GROQ_API_KEY", "").strip()
    )
    return raw.strip('"').strip("'")


def chat_model() -> str:
    raw = (os.getenv("CHAT_MODEL") or "openai/gpt-oss-20b").strip() or "openai/gpt-oss-20b"
    return DEAD_CHAT_MODELS.get(raw, raw)

def reply(user_text: str, language_id: str, history: list[dict]) -> str:
    if language_id not in SOUTH_AFRICAN_LANGUAGES:
        language_id = guess_language(user_text) or "english"
    api_key = _api_key()
    if api_key:
        try:
            from src.assistant import chat_turn

            return chat_turn(user_text, language_id, history, api_key)
        except Exception:
            traceback.print_exc()
            from src.tools import run_tool

            fallback = run_tool(user_text)
            if fallback:
                return fallback
            return (
                "Chat service failed. Check the Groq key in .env, restart app.py, "
                "and confirm OPENAI_BASE_URL is https://api.groq.com/openai/v1."
            )
    found = local_reply(user_text, language_id)
    if found:
        return found
    return _echo_in_language(user_text, language_id)


def openai_enabled() -> bool:
    return bool(_api_key())

def _echo_in_language(user_text: str, language_id: str) -> str:
    templates = {
        "english": "I heard: {text}. I can use your saved tasks and goals if Groq is on, or ask who I am, the time, or weather in a town.",
        "afrikaans": "Ek het gehoor: {text}. Vra wie ek is, wat ek kan doen, of die tyd.",
        "zulu": "Ngizwile: {text}. Ngibuze ukuthi ngingubani, ngenzeni, noma isikhathi.",
        "xhosa": "Ndivile: {text}. Ndibuze ukuba ndingubani, ndenza ntoni, okanye lixesha.",
        "sepedi": "Ke kwele: {text}. Mpotšiše gore ke mang, ke kgona go dira eng, goba nako ke efe.",
        "sesotho": "Ke u utloile: {text}. Mpotse hore na ke mang, ke khona ho etsa eng, kapa nako.",
        "setswana": "Ke utlwile: {text}. Mpotse gore ke mang, ke kgona go dira eng, kgotsa nako ke efe.",
        "tsonga": "Ndzi twile: {text}. Ndzi vutise leswaku ndzi mani, ndzi kota yini, kumbe nkarhi.",
        "swati": "Ngikuva: {text}. Ngibute kutsi ngingubani, ngenzeni, noma sikhatsi.",
        "venda": "Ndo u pfa: {text}. Mbudzisani uri ndi nnyi, ndi kona u ita mini, kana tshifhinga.",
        "ndebele": "Ngikuzwile: {text}. Ngibuze ukuthi ngingubani, ngenzeni, noma isikhathi.",
    }
    return templates.get(language_id, templates["english"]).format(text=user_text)
