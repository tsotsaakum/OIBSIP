from __future__ import annotations

import io

import speech_recognition as sr

from src.languages import AUTO_TRY_ORDER, SOUTH_AFRICAN_LANGUAGES


def transcribe_wav(wav_bytes: bytes, language_id: str) -> tuple[str, str]:
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
        audio = recognizer.record(source)

    if language_id != "auto" and language_id in SOUTH_AFRICAN_LANGUAGES:
        text = _google(recognizer, audio, SOUTH_AFRICAN_LANGUAGES[language_id].stt)
        return text, language_id

    last_error = None
    for lang_id in AUTO_TRY_ORDER:
        try:
            text = _google(recognizer, audio, SOUTH_AFRICAN_LANGUAGES[lang_id].stt)
            if text.strip():
                return text, lang_id
        except sr.UnknownValueError:
            continue
        except sr.RequestError as exc:
            last_error = exc
            break

    if last_error:
        raise RuntimeError("Speech service is unavailable. Check your internet connection.") from last_error
    raise RuntimeError("I could not catch that. Try again closer to the mic, or pick the language.")


def _google(recognizer: sr.Recognizer, audio: sr.AudioData, locale: str) -> str:
    return recognizer.recognize_google(audio, language=locale)
