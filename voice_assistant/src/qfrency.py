"""Use licensed CSIR Qfrency voices via Windows SAPI (pyttsx3).

We do not ship or download Qfrency. Install a trial or licence, then Lentswe
picks up the voices by name.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from src.languages import SOUTH_AFRICAN_LANGUAGES

_VOICE_CACHE: list | None = None


def qfrency_enabled() -> bool:
    return os.getenv("USE_QFRENCY", "1").strip().lower() not in {"0", "false", "no"}


def list_sapi_voices() -> list:
    global _VOICE_CACHE
    if _VOICE_CACHE is not None:
        return _VOICE_CACHE
    try:
        import pyttsx3
    except ImportError:
        _VOICE_CACHE = []
        return _VOICE_CACHE
    try:
        engine = pyttsx3.init()
        _VOICE_CACHE = list(engine.getProperty("voices") or [])
        engine.stop()
    except Exception:
        _VOICE_CACHE = []
    return _VOICE_CACHE


def qfrency_voice_id(language_id: str) -> str | None:
    if not qfrency_enabled():
        return None
    meta = SOUTH_AFRICAN_LANGUAGES.get(language_id)
    if not meta or not meta.qfrency_needles:
        return None
    voices = list_sapi_voices()
    if not voices:
        return None
    tagged = [v for v in voices if "qfrency" in _blob(v)]
    pool = tagged or voices
    for needle in meta.qfrency_needles:
        n = needle.lower()
        for voice in pool:
            if n in _blob(voice):
                return str(voice.id)
    return None


def installed_qfrency_languages() -> list[str]:
    return [key for key in SOUTH_AFRICAN_LANGUAGES if qfrency_voice_id(key)]


def speak_qfrency(text: str, language_id: str) -> bytes | None:
    voice_id = qfrency_voice_id(language_id)
    if not voice_id or not (text or "").strip():
        return None
    try:
        import pyttsx3
    except ImportError:
        return None
    path = None
    try:
        engine = pyttsx3.init()
        engine.setProperty("voice", voice_id)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            path = Path(tmp.name)
        engine.save_to_file(text, str(path))
        engine.runAndWait()
        data = path.read_bytes()
        return data if data else None
    except Exception:
        return None
    finally:
        if path:
            path.unlink(missing_ok=True)


def _blob(voice) -> str:
    name = getattr(voice, "name", "") or ""
    ident = getattr(voice, "id", "") or ""
    return f"{name} {ident}".lower()


def main() -> None:
    voices = list_sapi_voices()
    print(f"SAPI voices on this PC: {len(voices)}")
    for voice in voices:
        print("-", getattr(voice, "name", ""), "|", getattr(voice, "id", ""))
    print("Qfrency match per language:")
    for key, meta in SOUTH_AFRICAN_LANGUAGES.items():
        hit = qfrency_voice_id(key)
        print(f"  {meta.name}: {hit or 'not installed'}")


if __name__ == "__main__":
    main()
