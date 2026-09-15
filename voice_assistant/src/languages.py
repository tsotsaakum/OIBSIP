"""South Africa's 11 official languages — STT locales and TTS voices."""
from dataclasses import dataclass


@dataclass
class LanguageInfo:
    name: str
    native: str
    stt: str
    edge_tts_voice: str | None = None
    gtts_lang: str | None = None
    mms_code: str | None = None
    hf_tts_repos: tuple[str, ...] = ()
    voice_kind: str = "fallback"
    qfrency_needles: tuple[str, ...] = ()


SOUTH_AFRICAN_LANGUAGES: dict[str, LanguageInfo] = {
    "english": LanguageInfo(
        "English (South Africa)",
        "English",
        "en-ZA",
        edge_tts_voice="en-ZA-LeahNeural",
        gtts_lang="en",
        voice_kind="edge",
        qfrency_needles=("qfrency-english-candice", "candice", "qfrency-english-tim", "qfrency-english"),
    ),
    "afrikaans": LanguageInfo(
        "Afrikaans",
        "Afrikaans",
        "af-ZA",
        edge_tts_voice="af-ZA-AdriNeural",
        gtts_lang="af",
        hf_tts_repos=("UBC-NLP/Simba-TTS-afr",),
        voice_kind="edge",
        qfrency_needles=("maryna", "kobus", "bennie", "qfrency-afrikaans"),
    ),
    "zulu": LanguageInfo(
        "isiZulu",
        "isiZulu",
        "zu-ZA",
        edge_tts_voice="zu-ZA-ThandoNeural",
        gtts_lang="zu",
        voice_kind="edge",
        qfrency_needles=("lindiwe", "sifiso", "qfrency-isizulu", "qfrency-zulu"),
    ),
    "xhosa": LanguageInfo(
        "isiXhosa",
        "isiXhosa",
        "xh-ZA",
        gtts_lang="xh",
        hf_tts_repos=("UBC-NLP/Simba-TTS-xho",),
        voice_kind="simba",
        qfrency_needles=("zoleka", "vuyo", "qfrency-isixhosa", "qfrency-xhosa"),
    ),
    "sepedi": LanguageInfo(
        "Sepedi",
        "Sepedi",
        "nso-ZA",
        gtts_lang="nso",
        voice_kind="fallback",
        qfrency_needles=("mmapitsi", "tshepo", "qfrency-sepedi"),
    ),
    "sesotho": LanguageInfo(
        "Sesotho",
        "Sesotho",
        "st-ZA",
        hf_tts_repos=("UBC-NLP/Simba-TTS-sot",),
        voice_kind="simba",
        qfrency_needles=("kamohelo", "qfrency-sesotho"),
    ),
    "setswana": LanguageInfo(
        "Setswana",
        "Setswana",
        "tn-ZA",
        hf_tts_repos=("UBC-NLP/Simba-TTS-tsn",),
        voice_kind="simba",
        qfrency_needles=("lethabo", "qfrency-setswana"),
    ),
    "tsonga": LanguageInfo(
        "Xitsonga",
        "Xitsonga",
        "ts-ZA",
        mms_code="tso",
        hf_tts_repos=("facebook/mms-tts-tso",),
        voice_kind="mms",
        qfrency_needles=("sasekani", "qfrency-xitsonga", "qfrency-tsonga"),
    ),
    "swati": LanguageInfo(
        "siSwati",
        "siSwati",
        "ss-ZA",
        voice_kind="fallback",
        qfrency_needles=("temaswati", "qfrency-siswati", "qfrency-swati"),
    ),
    "venda": LanguageInfo(
        "Tshivenda",
        "Tshivenda",
        "ve-ZA",
        voice_kind="fallback",
        qfrency_needles=("rabelani", "qfrency-tshivenda", "qfrency-venda"),
    ),
    "ndebele": LanguageInfo(
        "isiNdebele",
        "isiNdebele",
        "nr-ZA",
        voice_kind="fallback",
        qfrency_needles=("banele", "qfrency-isindebele", "qfrency-ndebele"),
    ),
}

AUTO_TRY_ORDER = [
    "english",
    "afrikaans",
    "sepedi",
    "zulu",
    "xhosa",
    "setswana",
    "tsonga",
    "sesotho",
    "swati",
    "venda",
    "ndebele",
]


def public_language_list() -> list[dict]:
    from src.qfrency import qfrency_voice_id

    return [
        {
            "id": key,
            "name": meta.name,
            "native": meta.native,
            "spoken": True,
            "voice": "qfrency" if qfrency_voice_id(key) else meta.voice_kind,
        }
        for key, meta in SOUTH_AFRICAN_LANGUAGES.items()
    ]
