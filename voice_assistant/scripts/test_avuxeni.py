"""Xitsonga native TTS via local Meta MMS. Does not print secrets."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tts import speak  # noqa: E402


def main() -> int:
    audio = speak("Avuxeni", "tsonga")
    if not audio:
        print("result fail")
        return 1
    out = ROOT / "avuxeni-test.wav"
    out.write_bytes(audio)
    print("result ok")
    print("bytes", len(audio))
    print("riff", audio[:4] == b"RIFF")
    print("saved", out.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
