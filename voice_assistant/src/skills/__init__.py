"""Utility skills: travel, safety, health. Public SA numbers only — not medical advice."""


def travel_reply(user_text: str) -> str:
    from src.weather import is_pack_query, pack_for_trip

    if is_pack_query(user_text):
        return pack_for_trip(user_text)
    text = user_text.lower()
    if any(c in text for c in ("cape town", "kaapstad", "ct", "durban", "johannesburg", "joburg", "pretoria", "tshwane")):
        return pack_for_trip(user_text)
    return (
        "Travel with Lentswe: name a city, or say “what to pack for Durban”. "
        "I use live Open-Meteo — I do not book tickets. "
        "Share your live location with a person you trust, not with this app."
    )


def safety_reply() -> str:
    return (
        "South Africa emergency numbers (from any phone, including many lock screens):\n"
        "• 112 — emergency (cellphone)\n"
        "• 10111 — police (SAPS)\n"
        "• 10177 — ambulance\n"
        "If you are in immediate danger, call — do not only chat with me. "
        "I cannot send police or share your GPS."
    )


def health_reply(user_text: str) -> str:
    text = user_text.lower()
    if any(
        w in text
        for w in ("suicid", "kill myself", "end my life", "want to die", "self harm")
    ):
        return (
            "Please get human help now. In South Africa you can call SADAG on 0800 567 567 "
            "or emergency 112. I am a voice app, not a counsellor."
        )
    return (
        "Health: I am not a doctor and I will not diagnose you. "
        "Say “log that I have a headache” for a private symptom diary, or “show my symptoms”. "
        "Mental health: SADAG 0800 567 567. Emergency: 112."
    )


def music_reply() -> str:
    return (
        "Open the Music tab. Paste a Spotify playlist, album, or track link to embed it, "
        "or search YouTube Music. I do not play ripped files or clone a singer’s voice."
    )


def productivity_reply() -> str:
    return (
        "Productivity: add tasks in the Tasks panel, or say “add to my list buy bread”. "
        "Say “what’s on my list” to hear them. Tasks are saved in a local JSON file on this computer."
    )


def goals_reply() -> str:
    return (
        "Goals: say “my goal is save 500 this month” and “how am I doing on my goals”. "
        "I store them in a local JSON file. I do not upload your goals."
    )


def learning_reply(user_text: str) -> str:
    text = user_text.lower()
    lessons = {
        "zulu": "isiZulu: Sawubona is hello to one person. Sanibonani is hello to a group. Ngiyabonga is thank you.",
        "xhosa": "isiXhosa: Molo is hello to one person. Molweni is hello to a group. Enkosi is thank you.",
        "sepedi": "Sepedi: Dumela is hello to one person. Dumelang is hello to a group. Ke a leboga is thank you.",
        "afrikaans": "Afrikaans: Hallo is hello. Dankie is thank you. Totsiens is goodbye.",
    }
    for key, line in lessons.items():
        if key in text:
            return line + " Tap a greeting chip and listen to Lentswe’s synthetic voice — we do not copy YouTube audio."
    return (
        "Learning: I can drill SA greetings. Say “teach me isiZulu”, “teach me isiXhosa”, or “teach me Sepedi”. "
        "Or use Lentswe says all 11. This is practice, not a university course."
    )


def route_skill(user_text: str) -> str | None:
    text = user_text.lower()
    if any(
        w in text
        for w in (
            "emergency",
            "police",
            "ambulance",
            "10111",
            "10177",
            "safety",
            "not safe",
            "danger",
        )
    ):
        return safety_reply()
    if any(
        w in text
        for w in (
            "suicid",
            "kill myself",
            "sadag",
            "mental health",
            "wellbeing",
            "well-being",
            "drink water",
            "hydrate",
        )
    ) or ("health" in text and "weather" not in text):
        return health_reply(user_text)
    if any(w in text for w in ("teach me", "learn", "lesson", "practice greeting", "drill")):
        return learning_reply(user_text)
    if any(w in text for w in ("my goal", "goals", "new year", "ambition")):
        return goals_reply()
    if any(w in text for w in ("take me home", "directions home", "guide me home", "navigate home")):
        return (
            "Open the Home tab, then tap Guide me home. "
            "I do not store your GPS on a server."
        )
    if any(
        w in text
        for w in (
            "play music",
            "play a song",
            "play me a song",
            "spotify",
            "youtube music",
            "open music",
            "music tab",
        )
    ):
        return music_reply()
    if any(w in text for w in ("travel", "trip", "pack", "airport", "flight", "hike")):
        return travel_reply(user_text)
    if any(w in text for w in ("productivity", "be productive", "focus")):
        return productivity_reply()
    return None
