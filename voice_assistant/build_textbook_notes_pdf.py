"""Textbook-style Lentswe skill notes → PDF."""
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).resolve().parent / "Lentswe_Textbook_Notes.pdf"
INK = HexColor("#2c322e")
MUTE = HexColor("#4a5550")
SAGE = HexColor("#4a6b5c")
PAPER = HexColor("#faf8f4")
LINE = HexColor("#d8d3ca")
HEAD = HexColor("#e4ece6")


def styles():
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle(
            "cover",
            parent=base["Title"],
            fontName="Times-Bold",
            fontSize=22,
            textColor=SAGE,
            spaceAfter=6,
            leading=26,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="Times-Bold",
            fontSize=14,
            textColor=SAGE,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Times-Bold",
            fontSize=12,
            textColor=INK,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=10.5,
            leading=14.5,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=5,
        ),
        "note": ParagraphStyle(
            "note",
            parent=base["BodyText"],
            fontName="Times-Italic",
            fontSize=10,
            leading=13.5,
            textColor=MUTE,
            spaceAfter=8,
        ),
        "code": ParagraphStyle(
            "code",
            fontName="Courier",
            fontSize=8,
            leading=11,
            textColor=INK,
            backColor=PAPER,
            leftIndent=4,
            rightIndent=4,
            spaceBefore=3,
            spaceAfter=7,
        ),
        "cell": ParagraphStyle(
            "cell",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=9,
            leading=12,
            textColor=INK,
        ),
    }


def P(text, st):
    return Paragraph(text.replace("\n", "<br/>"), st)


def code_block(text, st):
    return Preformatted(text.strip("\n"), st)


def table(rows, widths, st):
    data = []
    for i, row in enumerate(rows):
        cells = []
        for cell in row:
            if i == 0:
                cells.append(P(f"<b>{cell}</b>", st["cell"]))
            else:
                cells.append(P(cell, st["cell"]))
        data.append(cells)
    t = Table(data, colWidths=widths)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), HEAD),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def bullets(items, st):
    return ListFlowable(
        [ListItem(P(item, st["body"]), leftIndent=12, bulletColor=SAGE) for item in items],
        bulletType="bullet",
        start="•",
        leftIndent=18,
        bulletFontName="Times-Roman",
        bulletFontSize=10,
    )


def build():
    st = styles()
    story = []

    story.append(P("Lentswe — textbook notes", st["cover"]))
    story.append(P("Voice assistants, tools, and honest speech systems", st["note"]))
    story.append(
        P(
            "A voice assistant is not one AI. It is a <b>pipeline</b>: speech in, text reasoning, "
            "tools, speech out. Lentswe is a small, honest version of that pipeline. "
            "These notes are for skill-building, not for copying into an assignment as your own theory.",
            st["body"],
        )
    )

    story.append(P("1. The pipeline (memorise this)", st["h1"]))
    story.append(
        code_block(
            "microphone  →  STT  →  brain  →  tools / LLM  →  TTS  →  speaker\n"
            "   (WAV)      (text)   (text)      (facts)       (audio)",
            st["code"],
        )
    )
    story.append(
        table(
            [
                ["Stage", "Full name", "Lentswe file", "Job"],
                ["STT", "Speech-to-text", "src/stt.py", "Sound → words"],
                ["NLU / brain", "Natural language understanding", "src/brain.py", "Decide what the user meant"],
                ["Tools", "Side effects", "store, weather, mail, browse", "Do things; do not guess"],
                ["LLM", "Large language model", "src/assistant.py + Groq", "Conversation + function calling"],
                ["TTS", "Text-to-speech", "src/tts.py", "Words → sound"],
                ["UI", "Client", "static/app.js", "Mic, chat, play audio"],
            ],
            [28 * mm, 48 * mm, 52 * mm, 52 * mm],
            st,
        )
    )
    story.append(Spacer(1, 6))
    story.append(
        P(
            "<b>Rule:</b> never invent a number a tool could have fetched (weather °C, "
            "“email sent”, “I called the police”).",
            st["body"],
        )
    )

    story.append(P("2. Client versus server", st["h1"]))
    story.append(
        P(
            "The <b>browser</b> must not hold your Groq key. It records audio and plays audio. "
            "The <b>Flask app</b> (<font face='Courier'>app.py</font>) is the server: it transcribes, thinks, and speaks.",
            st["body"],
        )
    )
    story.append(
        table(
            [
                ["Route", "Method", "Purpose"],
                ["/", "GET", "HTML page"],
                ["/api/talk", "POST", "Audio in; transcript + reply out"],
                ["/api/chat", "POST", "Typed text"],
                ["/api/speak", "POST", "TTS only"],
            ],
            [40 * mm, 28 * mm, 112 * mm],
            st,
        )
    )
    story.append(Spacer(1, 6))
    story.append(
        P(
            "Opening <font face='Courier'>/api/chat</font> in the address bar is a GET. "
            "That route is POST-only. Use the Lentswe page, not the raw API URL. "
            "<b>Skill:</b> GET = read; POST = send a body (JSON or files).",
            st["body"],
        )
    )

    story.append(P("3. Why brain.py is a ladder, not a blob", st["h1"]))
    story.append(
        P(
            "<font face='Courier'>think()</font> is a <b>priority cascade</b>: the first match wins.",
            st["body"],
        )
    )
    story.append(
        bullets(
            [
                "Wake phrase only → greeting",
                "Emergency keywords → SADAG / 10111 text (no dispatch)",
                "Clock, stop, volume",
                "Timed reminder, custom command, email",
                "Pack / run / music / Google search",
                "If a Groq key exists → keyword tools, then the LLM",
                "Else local weather / tools / skills",
            ],
            st,
        )
    )
    story.append(
        P(
            "<b>Why order matters.</b> If Groq ran first, “should I run today” used to echo the user "
            "when the API failed. Local intercepts (<font face='Courier'>is_run_query</font>) protect you "
            "from a dead model. <b>Skill:</b> control flow and fail closed. Prefer a small deterministic "
            "handler over a smart model that can lie.",
            st["body"],
        )
    )

    story.append(P("4. Two kinds of understanding", st["h1"]))
    story.append(P("A. Keywords and regular expressions (cheap, reliable)", st["h2"]))
    story.append(
        P(
            "Examples: <font face='Courier'>remind me in (\\d+)\\s*(minutes?)</font>, "
            "“weather in Cape Town”. Fast, no API cost. Breaks on paraphrase "
            "(“in a bit, ping me about water”).",
            st["body"],
        )
    )
    story.append(P("B. LLM plus tools (flexible, dangerous)", st["h2"]))
    story.append(
        P(
            "Groq gets a <b>system prompt</b> (persona, scope, ambiguity) and a list of <b>functions</b> "
            "(<font face='Courier'>get_weather</font>, <font face='Courier'>add_task</font>, "
            "<font face='Courier'>send_email</font>, …). The model must <b>call the tool</b>; "
            "it must not invent °C.",
            st["body"],
        )
    )
    story.append(
        P(
            "<b>Skill:</b> function calling means the model outputs a name and arguments; "
            "<i>your</i> Python runs <font face='Courier'>execute_tool()</font>. "
            "The model never touches the filesystem or SMTP itself.",
            st["body"],
        )
    )

    story.append(P("5. Memory: session versus lasting", st["h1"]))
    story.append(
        table(
            [
                ["Kind", "Where", "Survives refresh?"],
                ["Chat history", "JSON list in the browser, sent each request", "No (unless you persist it)"],
                ["Lasting notes", "data/lentswe.json via src/store.py", "Yes"],
                ["Home / Spotify", "browser localStorage", "Yes, this browser only"],
            ],
            [36 * mm, 78 * mm, 66 * mm],
            st,
        )
    )
    story.append(Spacer(1, 6))
    story.append(
        P(
            "<font face='Courier'>store.py</font> pattern: <font face='Courier'>load()</font> → mutate a dict → "
            "<font face='Courier'>save()</font>. That is CRUD on a JSON file: Create, Read, Update, Delete. "
            "A product would often use SQLite; the idea is the same. "
            "<b>Skill:</b> gitignore secrets and user data (<font face='Courier'>.env</font>, "
            "<font face='Courier'>lentswe.json</font>).",
            st["body"],
        )
    )

    story.append(P("6. Configuration and secrets", st["h1"]))
    story.append(
        P(
            "<font face='Courier'>.env</font> is not source code. <font face='Courier'>python-dotenv</font> loads it. "
            "Empty environment variables can override the file unless you use "
            "<font face='Courier'>override=True</font> — that bug hid the Groq key for a long time.",
            st["body"],
        )
    )
    story.append(
        table(
            [
                ["Variable", "Meaning"],
                ["OPENAI_API_KEY", "Groq key (the name is historical)"],
                ["OPENAI_BASE_URL", "https://api.groq.com/openai/v1"],
                ["CHAT_MODEL", "Must be a live model id"],
                ["SMTP_*", "Optional; never pretend a send succeeded"],
                ["HF_TOKEN", "Optional Hugging Face downloads"],
            ],
            [48 * mm, 132 * mm],
            st,
        )
    )
    story.append(Spacer(1, 6))
    story.append(
        P(
            "<b>Skill:</b> 12-factor config — credentials in the environment, not in Git.",
            st["body"],
        )
    )

    story.append(P("7. Text-to-speech: a fallback stack", st["h1"]))
    story.append(P("<font face='Courier'>speak()</font> tries in order:", st["body"]))
    story.append(
        bullets(
            [
                "Qfrency (Windows SAPI) if the licensed voice is installed",
                "Microsoft Edge neural voices (en-ZA, af-ZA, zu-ZA)",
                "Simba / MMS (local VITS via torch)",
                "gTTS / multilingual Edge / pyttsx3",
            ],
            st,
        )
    )
    story.append(
        P(
            "<b>Concept:</b> graceful degradation. The app stays audible even if one vendor is down. "
            "<b>Ethics:</b> a native voice means a model trained for that language, not a YouTube clone. "
            "If no public checkpoint exists (Sepedi, siSwati, Tshivenda, isiNdebele on the Hub), "
            "say so and use Qfrency or a labelled fallback. Honesty is part of the engineering.",
            st["body"],
        )
    )

    story.append(P("8. Speech recognition", st["h1"]))
    story.append(
        P(
            "The browser records WAV → Flask → <font face='Courier'>speech_recognition</font> + Google STT "
            "with <font face='Courier'>*-ZA</font> locales. That needs internet. Click-to-talk is a privacy choice: "
            "not always-on wake-word hardware. <b>Skill:</b> WAV versus MP3. TTS may return WAV (SAPI, MMS) "
            "or MP3 (Edge). The player must accept both.",
            st["body"],
        )
    )

    story.append(P("9. APIs used in Lentswe", st["h1"]))
    story.append(
        table(
            [
                ["Need", "Service", "Key?"],
                ["Chat", "Groq (OpenAI-compatible)", "Yes"],
                ["Weather", "Open-Meteo", "No"],
                ["Geocode", "Nominatim (OpenStreetMap)", "No (polite User-Agent)"],
                ["Driving", "OpenRouteService", "Optional"],
                ["Search page", "webbrowser + Google URL", "No"],
                ["Facts", "Wikipedia API (web_search.py)", "No"],
                ["Mail", "smtplib + STARTTLS", "Yes, SMTP"],
            ],
            [36 * mm, 88 * mm, 56 * mm],
            st,
        )
    )
    story.append(Spacer(1, 6))
    story.append(
        P(
            "<b>Skill:</b> REST is HTTP plus JSON. 200 = ok, 400 = your request, 404 = missing, 503 = upstream down.",
            st["body"],
        )
    )

    story.append(P("10. Flask, briefly", st["h1"]))
    story.append(
        code_block(
            "@app.post(\"/api/chat\")\n"
            "def chat():\n"
            "    body = request.get_json()\n"
            "    reply = think(...)\n"
            "    return jsonify({\"reply\": reply})",
            st["code"],
        )
    )
    story.append(
        P(
            "Decorators bind a URL and method to a function. <font face='Courier'>jsonify</font> sets "
            "<font face='Courier'>Content-Type: application/json</font>. "
            "Use <font face='Courier'>venv\\Scripts\\python.exe</font> so packages do not fight system Python.",
            st["body"],
        )
    )

    story.append(P("11. Bugs worth remembering", st["h1"]))
    story.append(
        bullets(
            [
                "Returning the user message in except → the assistant repeats you. Return an error sentence.",
                "Duplicate Flask routes with the same path → AssertionError.",
                "IndentationError or SyntaxError in any imported module → the whole server dies.",
                "Dead model ids (for example a shut-down Llama instant model) → alias or fail clearly.",
                "load_dotenv without override → an empty env var wins over .env.",
                "Git identity missing → commit fails. Never commit .env.",
            ],
            st,
        )
    )

    story.append(P("12. Privacy (exam paragraph)", st["h1"]))
    story.append(
        P(
            "Audio is sent to Google STT. Chat may be sent to Groq. Tasks live on disk. "
            "Home address stays in the browser. SMTP only if configured. No SMS, no police call, "
            "no medical diagnosis. That is <b>scope control</b>, not a missing feature.",
            st["body"],
        )
    )

    story.append(P("13. Skills to practise next", st["h1"]))
    story.append(
        P(
            "1. Python: functions, pathlib, regex, try/except, dataclasses.<br/>"
            "2. HTTP: fetch in JavaScript, Flask routes, JSON.<br/>"
            "3. State: JSON file, then SQLite.<br/>"
            "4. Prompting: system versus user versus tool messages.<br/>"
            "5. Testing: one function, one assert.<br/>"
            "6. Git: small commits; never commit <font face='Courier'>.env</font>.",
            st["body"],
        )
    )

    story.append(P("14. Check yourself", st["h1"]))
    story.append(
        P(
            "1. Draw the pipeline from mic to speaker and name four files.<br/>"
            "2. Why must weather use a tool, not the LLM’s memory?<br/>"
            "3. What is the difference between localStorage and lentswe.json?<br/>"
            "4. Why does Qfrency live outside the GitHub repo?<br/>"
            "5. If Groq is down, which user questions still work?",
            st["body"],
        )
    )

    story.append(P("15. One-sentence summary", st["h1"]))
    story.append(
        P(
            "Lentswe is a Flask voice assistant that turns speech into text, routes intent through "
            "a priority brain, uses tools for facts and side effects, and speaks back through a stack "
            "of licensed or public TTS — without claiming powers it does not have.",
            st["body"],
        )
    )
    story.append(
        P(
            "When you build the next assistant, copy the pipeline and the honesty rules, not the file names.",
            st["note"],
        )
    )

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="Lentswe Textbook Notes",
        author="Lentswe study notes",
    )
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    build()
