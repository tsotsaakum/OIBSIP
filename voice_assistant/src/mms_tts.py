"""Local VITS TTS: Meta MMS where the Hub has a checkpoint, else UBC Simba-TTS.

These are trained synthetic voices — not YouTube clones.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

_MODELS: dict[str, tuple] = {}
_MISSING: set[str] = set()


def speak_native(text: str, repos: tuple[str, ...] | list[str] | None) -> bytes | None:
    if not text or not repos:
        return None
    for repo in repos:
        audio = _speak_repo(text, repo)
        if audio:
            return audio
    return None


def speak_mms(text: str, mms_code: str | None) -> bytes | None:
    """Back-compat: facebook/mms-tts-{code} when that repo exists (Xitsonga tso)."""
    if not mms_code:
        return None
    return speak_native(text, (f"facebook/mms-tts-{mms_code}",))


def _speak_repo(text: str, repo: str) -> bytes | None:
    if not repo or repo in _MISSING:
        return None
    import scipy.io.wavfile
    import torch
    from transformers import AutoTokenizer, VitsModel

    if repo not in _MODELS:
        token = os.getenv("HF_TOKEN", "").strip() or None
        try:
            model = VitsModel.from_pretrained(repo, token=token)
            tokenizer = AutoTokenizer.from_pretrained(repo, token=token)
        except Exception:
            _MISSING.add(repo)
            return None
        _MODELS[repo] = (model, tokenizer)

    model, tokenizer = _MODELS[repo]
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        waveform = model(**inputs).waveform
    data = waveform.squeeze().cpu().numpy()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        path = Path(tmp.name)
    try:
        scipy.io.wavfile.write(path, rate=model.config.sampling_rate, data=data)
        return path.read_bytes()
    finally:
        path.unlink(missing_ok=True)
