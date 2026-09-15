from __future__ import annotations

from datetime import datetime

# Small, honest local brain: greetings, identity, time, help.
# OpenAI (if a key is in .env) handles everything else.


def local_reply(user_text: str, language_id: str) -> str | None:
    text = user_text.lower().strip()
    now = datetime.now().strftime("%H:%M")

    language_id = guess_language(text) or language_id

    if _is_greeting(text):
        opening = _native_greeting(text, language_id)
        follow = {
            "english": "I'm Lentswe, your South African voice assistant.",
            "afrikaans": "Ek is Lentswe, jou Suid-Afrikaanse stem-assistent.",
            "zulu": "Ngingu-Lentswe.",
            "xhosa": "Ndingu-Lentswe.",
            "sepedi": "Ke nna Lentswe.",
            "sesotho": "Ke Lentswe.",
            "setswana": "Ke nna Lentswe.",
            "tsonga": "Ndzi Lentswe.",
            "swati": "Ngingu-Lentswe.",
            "venda": "Ndi Lentswe.",
            "ndebele": "Ngingu-Lentswe.",
        }.get(language_id, "I'm Lentswe.")
        return f"{opening} {follow}"

    if _is_how_are_you(text):
        return {
            "english": "I'm sharp, thanks. How are you doing today?",
            "afrikaans": "Dit gaan lekker, dankie. Hoe gaan dit met jou?",
            "zulu": "Ngiyaphila, ngiyabonga. Unjani wena namuhla?",
            "xhosa": "Ndiyaphila, enkosi. Unjani wena namhlanje?",
            "sepedi": "Ke phela gabotse, ke a leboga. Wena o kae namhlanje?",
            "sesotho": "Ke phela hantle, ke a leboha. Wena o kae kajeno?",
            "setswana": "Ke tsogile sentle, ke a leboga. Wena o tsogile jang gompieno?",
            "tsonga": "Ndzi hanyi kahle, ndza khensa. Wena u njhani namuntlha?",
            "swati": "Ngiyaphila, ngiyabonga. Unjani wena namuhla?",
            "venda": "Ndi khou tshila zwavhudi. Inwi ni khou tshila hani namusi?",
            "ndebele": "Ngiyaphila, ngiyathokoza. Unjani wena namhlanje?",
        }.get(language_id)

    if _is_who(text):
        return {
            "english": "I'm Lentswe. I listen in South African accents and reply in the language you pick — including Sepedi, isiXhosa and Setswana.",
            "afrikaans": "Ek is Lentswe. Ek luister na Suid-Afrikaanse aksente en antwoord in die taal wat jy kies.",
            "zulu": "Ngingu-Lentswe. Ngiyalalela izilimi zaseNingizimu Afrika, ngiphendule ngolimi olukhethile.",
            "xhosa": "Ndingu-Lentswe. Ndiyalalela iilwimi zaseMzantsi Afrika, ndiphendule ngolwimi olukhethileyo.",
            "sepedi": "Ke nna Lentswe. Ke kwešiša maemedi a Afrika Borwa, ke araba ka polelo ye o e kgethilego — go akaretša Sepedi.",
            "sesotho": "Ke Lentswe. Ke mamela lipuo tsa Afrika Borwa, ke arabe ka puo eo u e khethileng.",
            "setswana": "Ke nna Lentswe. Ke utlwa dipuo tsa Aforika Borwa, ke arabe ka puo e o e tlhophileng — go akaretsa Setswana.",
            "tsonga": "Ndzi Lentswe. Ndzi twisisa tindzimi ta Afrika-Dzonga, ndzi hlamula hi ririmi leri u ri hlawuleke.",
            "swati": "Ngingu-Lentswe. Ngiyalalela tilwimi taseNingizimu Afrika.",
            "venda": "Ndi Lentswe. Ndi thetshelesa nyambo dza Afrika Tshipembe.",
            "ndebele": "Ngingu-Lentswe. Ngiyalalela iilwimi zaseSewula Afrika.",
        }.get(language_id)

    if _is_help(text) or _is_languages(text):
        return {
            "english": "Pick a language, then talk or type. I can greet in 11 languages, weather, travel tips, SA emergency numbers, a to-do list, and wellbeing helplines. I am not a doctor and I cannot call the police for you.",
            "afrikaans": "Kies 'n taal, hou die mikrofoon in, en praat. Jy kan ook tik.",
            "zulu": "Khetha ulimi, bamba imakrofoni, bese ukhuluma. Ungabhala futhi.",
            "xhosa": "Khetha ulwimi, bamba imakrofoni, uze uthethe. Ungabhala kwakhona.",
            "sepedi": "Kgetha polelo, swara maekrofounu, o bolele. O ka ngwala gape. Bakeng sa Sepedi, kgetha Sepedi pele o bolela.",
            "sesotho": "Khetha puo, tšoara maekrofounu, ebe u bua. U ka ngola hape.",
            "setswana": "Tlhopha puo, tshwara maekrofounu, mme o bue. O ka kwala gape. Bakeng sa Setswana, tlhopha Setswana pele o bua.",
            "tsonga": "Hlawula ririmi, khoma makhrofoni, u vulavula.",
            "swati": "Khetsa lulwimi, bamba imakrofoni, bese ukhuluma.",
            "venda": "Nangani luambo, farani maikirofoni, ni ambe.",
            "ndebele": "Khetha ilimi, bamba imakrofoni, bese ukhuluma.",
        }.get(language_id)

    if _is_time(text):
        return {
            "english": f"It's {now} right now.",
            "afrikaans": f"Dit is nou {now}.",
            "zulu": f"Yisikhathi esingu-{now} manje.",
            "xhosa": f"Lixesha elingu-{now} ngoku.",
            "sepedi": f"Nako ke {now} gabjale.",
            "sesotho": f"Nako ke {now} hona joale.",
            "setswana": f"Nako ke {now} jaanong.",
            "tsonga": f"Nkarhi i {now} sweswi.",
            "swati": f"Sikhatsi ngu-{now} nyalo.",
            "venda": f"Tshifhinga ndi {now} zwino.",
            "ndebele": f"Yisikhathi esingu-{now} khathesi.",
        }.get(language_id)

    if _is_thanks(text):
        return {
            "english": "Pleasure. I'm here if you need me.",
            "afrikaans": "Graag. Ek is hier as jy my nodig het.",
            "zulu": "Ngiyabonga. Ngilapha uma ungidinga.",
            "xhosa": "Enkosi. Ndilapha xa undidinga.",
            "sepedi": "Ke a leboga. Ke gona ge o ntlhoka.",
            "sesotho": "Ke a leboha. Ke teng ha u ntlhoka.",
            "setswana": "Ke a leboga. Ke fano fa o ntlhoka.",
            "tsonga": "Ndza khensa. Ndzi kona loko u ndzi lava.",
            "swati": "Ngiyabonga. Ngilapha uma ungidinga.",
            "venda": "Ndo livhuwa. Ndi hone arali ni ntodou.",
            "ndebele": "Ngiyathokoza. Ngilapha nxa ungidinga.",
        }.get(language_id)

    return None


# Native greetings from Jabu: https://www.youtube.com/watch?v=snVTKXcGvuY
# Singular / plural where he taught both.


def _native_greeting(text: str, language_id: str) -> str:
    plural = any(
        w in text
        for w in ("sanibonani", "sanbonani", "molweni", "dumelang")
    )
    table = {
        "english": ("Hello", "Hello"),
        "afrikaans": ("Hallo", "Hallo"),
        "xhosa": ("Molo", "Molweni"),
        "zulu": ("Sawubona", "Sanibonani"),
        "swati": ("Sawubona", "Sanibonani"),
        "sepedi": ("Dumela", "Dumelang"),
        "sesotho": ("Dumela", "Dumelang"),
        "setswana": ("Dumela", "Dumelang"),
        "tsonga": ("Avuxeni", "Avuxeni"),
        "venda": ("Ndaa", "Ndaa"),
        "ndebele": ("Lotjhani", "Lotjhani"),
    }
    if "aah" in text.split() or text.strip() in {"aah", "aa", "a"}:
        return "Aah"
    one, many = table.get(language_id, ("Hello", "Hello"))
    return many if plural else one


def guess_language(text: str) -> str | None:
    if any(w in text for w in ("sawubona", "sanibonani", "sanbonani", "sanibona")):
        return "zulu"
    if "molo" in text or "molweni" in text:
        return "xhosa"
    if "avuxeni" in text:
        return "tsonga"
    if "lotjhani" in text:
        return "ndebele"
    if "ndaa" in text or text.strip() in {"aah", "aa"}:
        return "venda"
    if "dumelang" in text or "dumela" in text:
        return "sepedi"
    if "hallo" in text:
        return "afrikaans"
    if "hello" in text or "howzit" in text:
        return "english"
    return None


def _is_greeting(text: str) -> bool:
    cues = (
        "hello", "hi", "hey", "howzit", "hallo", "goeie", "sawubona", "molo",
        "dumela", "dumelang", "avuxeni", "ndaa", "lotjhani", "sanibonani",
        "sanbonani", "sanibona", "molweni",
    )
    if text.strip() in {"aah", "aa"}:
        return True
    return any(c in text for c in cues) and len(text.split()) <= 8


def _is_how_are_you(text: str) -> bool:
    return any(
        p in text
        for p in (
            "how are you", "howzit going", "hoe gaan dit", "unjani", "o kae",
            "o tsogile", "u njhani", "o phela", "kunjani",
        )
    )


def _is_who(text: str) -> bool:
    return any(
        p in text
        for p in (
            "who are you", "your name", "wie is jy", "ungubani",
            "ke mang", "o mang", "leina", "igama", "ngubani", "what are you",
        )
    )


def _is_help(text: str) -> bool:
    return any(p in text for p in ("help", "thušo", "thuso", "nceda", "siza", "how do i", "what can you"))


def _is_languages(text: str) -> bool:
    return any(
        p in text
        for p in (
            "language", "tale", "ilwimi", "dipolelo", "dipuo", "tindzimi",
            "sepedi", "xhosa", "setswana", "tswana", "support",
        )
    )


def _is_time(text: str) -> bool:
    return any(p in text for p in ("time", "nako", "ixesha", "isikhathi", "nkarhi", "tshifhinga", "what time"))


def _is_thanks(text: str) -> bool:
    return any(
        p in text
        for p in ("thank", "dankie", "leboga", "leboha", "ngiyabonga", "enkosi", "khensa", "livhuwa", "thokoza")
    )
