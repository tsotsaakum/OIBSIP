"""Build a handwriting-friendly study PDF of the Lentswe UI code."""
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).resolve().parent / "Lentswe_UI_Study_Notes.pdf"
INK = HexColor("#2c322e")
MUTE = HexColor("#4a5550")
SAGE = HexColor("#4a6b5c")
PAPER = HexColor("#faf8f4")
LINE = HexColor("#d8d3ca")


def styles():
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle(
            "cover",
            parent=base["Title"],
            fontName="Times-Bold",
            fontSize=22,
            textColor=SAGE,
            spaceAfter=8,
            leading=26,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="Times-Bold",
            fontSize=16,
            textColor=SAGE,
            spaceBefore=12,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Times-Bold",
            fontSize=13,
            textColor=INK,
            spaceBefore=10,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=11,
            leading=15,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "note": ParagraphStyle(
            "note",
            parent=base["BodyText"],
            fontName="Times-Italic",
            fontSize=10,
            leading=14,
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
            spaceBefore=4,
            spaceAfter=8,
        ),
    }


def P(text, st):
    return Paragraph(text.replace("\n", "<br/>"), st)


def code_block(text, st):
    return Preformatted(text.strip("\n"), st)


def build():
    st = styles()
    story = []

    story.append(P("Lentswe — UI study notes", st["cover"]))
    story.append(P("Write this by hand. HTML first, then CSS tokens, then every JavaScript function.", st["note"]))
    story.append(P(
        "There is no PHP and no database in this project. The page is HTML + CSS. "
        "Clicks and the mic are JavaScript (<font face='Courier'>static/app.js</font>). "
        "Speech and answers are Python Flask (<font face='Courier'>app.py</font>).",
        st["body"],
    ))

    story.append(P("1. The three files", st["h1"]))
    data = [
        [P("<b>File</b>", st["body"]), P("<b>Language</b>", st["body"]), P("<b>Job</b>", st["body"])],
        [P("static/index.html", st["body"]), P("HTML", st["body"]), P("The page: headings, mic, form, ids.", st["body"])],
        [P("static/styles.css", st["body"]), P("CSS", st["body"]), P("Look: colours, fonts, layout.", st["body"])],
        [P("static/app.js", st["body"]), P("JavaScript", st["body"]), P("Behaviour: talk, send, greetings.", st["body"])],
    ]
    t = Table(data, colWidths=[42 * mm, 28 * mm, 110 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#e4ece6")),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))
    story.append(P(
        "JavaScript finds elements with <font face='Courier'>getElementById</font>. "
        "If you rename an id in HTML, the function that uses it will break.",
        st["body"],
    ))

    story.append(P("2. HTML ids you must not rename", st["h1"]))
    ids = [
        ("language", "Dropdown of the 11 languages. JS fills extra options."),
        ("spoken-hint", "Sentence under the header about speech vs text."),
        ("play-all", "Button that plays all 11 greetings one after another."),
        ("greet-chips", "Empty div. JS inserts Hello / Sawubona / Dumela buttons."),
        ("log", "Chat area. Bubbles are added inside this section."),
        ("empty-state", "First message. Removed after the first bubble."),
        ("type-form", "The form. Submit sends typed text."),
        ("mic", "Click to record, click again to send audio."),
        ("text-input", "The type box."),
        ("stop-speech", "Hides until she is talking. Stops playback."),
        ("status", "Ready / Listening / Transcribing."),
    ]
    rows = [[P("<b>id</b>", st["body"]), P("<b>What it is for</b>", st["body"])]]
    for i, why in ids:
        rows.append([P(f"<font face='Courier'>{i}</font>", st["body"]), P(why, st["body"])])
    t2 = Table(rows, colWidths=[40 * mm, 140 * mm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#e4ece6")),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)

    story.append(P("3. Full HTML (static/index.html)", st["h1"]))
    story.append(P(
        "Copy this file from the top. The crest is an SVG picture. "
        "class names (page, top, dock, mic) are only for CSS. ids are for JavaScript.",
        st["note"],
    ))
    html = Path(__file__).resolve().parent.joinpath("static", "index.html").read_text(encoding="utf-8")
    story.append(code_block(html, st["code"]))

    story.append(PageBreak())
    story.append(P("4. CSS colour tokens (top of static/styles.css)", st["h1"]))
    story.append(P(
        "These are variables. The rest of the CSS says var(--clay) instead of a hex each time. "
        "Change a token, the whole page follows.",
        st["body"],
    ))
    story.append(code_block(
        """:root {
  --soil: #2c322e;   /* dark text / earth */
  --clay: #c48b8a;   /* dusty pink: Send, listening */
  --sand: #f3f0ea;   /* pale fill */
  --leaf: #4a6b5c;   /* sage: mic, your bubbles */
  --ink: #2c322e;    /* main words */
  --mute: #6b736e;   /* quieter words */
  --user: #4a6b5c;   /* your chat bubble */
  --bot: #6d5a5a;    /* Lentswe's bubble */
  --line: #d8d3ca;   /* thin borders */
  --paper: #faf8f4;  /* cards and dock */
}""",
        st["code"],
    ))
    story.append(P(
        "body uses Source Sans 3. h1 and greetings use Fraunces (serif). "
        ".mic.hot turns the mic pink while you record. "
        "Write down :root first; you do not need every CSS rule by hand unless asked.",
        st["body"],
    ))

    story.append(P("5. JavaScript — variables at the top of app.js", st["h1"]))
    story.append(P(
        "These are not functions. They hold the page pieces and the conversation.",
        st["body"],
    ))
    story.append(code_block(
        """const languageSelect = document.getElementById("language");
const micButton = document.getElementById("mic");
const statusEl = document.getElementById("status");
const logEl = document.getElementById("log");
const form = document.getElementById("type-form");
const textInput = document.getElementById("text-input");
const spokenHint = document.getElementById("spoken-hint");
const stopSpeechBtn = document.getElementById("stop-speech");
const emptyState = document.getElementById("empty-state");
const history = [];           // chat turns sent to Python
const languagesById = new Map();
let recorder = null;          // MediaRecorder
let chunks = [];              // audio pieces
let recording = false;
let currentAudio = null;      // playing reply""",
        st["code"],
    ))
    story.append(P(
        "JABU_GREETINGS is a list of 11 objects: lang, say, word, langLabel. "
        "That is the data for the greeting chips.",
        st["body"],
    ))

    funcs = [
        (
            "setStatus(text)",
            """function setStatus(text) {
  statusEl.textContent = text;
}""",
            "Puts a sentence in the status line (Ready, Listening, Transcribing). One job: update text on screen.",
        ),
        (
            "hideEmpty()",
            """function hideEmpty() {
  emptyState?.remove();
}""",
            "Deletes the empty-state box. ?. means: if emptyState is missing, do nothing. Called before the first bubble.",
        ),
        (
            "addBubble(role, text, caption)",
            """function addBubble(role, text, caption) {
  hideEmpty();
  const div = document.createElement("div");
  div.className = `bubble ${role}`;
  if (caption) {
    const small = document.createElement("small");
    small.textContent = caption;
    div.appendChild(small);
  }
  div.appendChild(document.createTextNode(text));
  logEl.appendChild(div);
  logEl.scrollTop = logEl.scrollHeight;
}""",
            "Draws one chat bubble. role is \"user\" or \"bot\" (CSS colours). caption is the small label (You / Lentswe). Scrolls the log to the bottom.",
        ),
        (
            "updateSpokenHint()",
            """function updateSpokenHint() {
  if (!spokenHint) return;
  const id = languageSelect.value;
  if (id === "auto") { /* auto message */ return; }
  const meta = languagesById.get(id);
  spokenHint.textContent = meta.spoken
    ? `${meta.name} can speak back as well as show text.`
    : `${meta.name} replies as text for now.`;
}""",
            "Updates the hint when the language dropdown changes. Tells you if that language has a spoken voice.",
        ),
        (
            "loadLanguages()  [async]",
            """async function loadLanguages() {
  const res = await fetch("/api/languages");
  const data = await res.json();
  for (const lang of data.languages) {
    languagesById.set(lang.id, lang);
    const opt = document.createElement("option");
    opt.value = lang.id;
    opt.textContent = lang.spoken ? lang.name : `${lang.name} (text)`;
    languageSelect.appendChild(opt);
  }
  updateSpokenHint();
}""",
            "Asks Python GET /api/languages. Adds each language to the dropdown. async/await waits for the network without freezing the page.",
        ),
        (
            "encodeWav(audioBuffer)",
            """function encodeWav(audioBuffer) {
  /* reads samples, writes a 44-byte WAV header, then 16-bit PCM */
  return new Blob([buffer], { type: "audio/wav" });
}""",
            "Turns decoded microphone audio into a .wav Blob. Python SpeechRecognition expects WAV. The full header bytes are in app.js — for the exam, write: it builds a WAV file in memory.",
        ),
        (
            "blobToWav(blob)  [async]",
            """async function blobToWav(blob) {
  const ctx = new AudioContext();
  const arrayBuffer = await blob.arrayBuffer();
  const audioBuffer = await ctx.decodeAudioData(arrayBuffer);
  const wav = encodeWav(audioBuffer);
  await ctx.close();
  return wav;
}""",
            "The browser records webm/opus. This decodes that blob, then encodeWav makes WAV.",
        ),
        (
            "sendAudio(blob)  [async]",
            """async function sendAudio(blob) {
  setStatus("Transcribing…");
  const wav = await blobToWav(blob);
  const formData = new FormData();
  formData.append("audio", wav, "speech.wav");
  formData.append("language", languageSelect.value);
  formData.append("history_json", JSON.stringify(history));
  const res = await fetch("/api/talk", { method: "POST", body: formData });
  const data = await res.json();
  /* add bubbles, maybe speak, or stop if user said thula */
}""",
            "POSTs the recording to /api/talk. Python transcribes and replies. Adds two bubbles, then maybeSpeak. If the transcript is stop/thula/khutsa, it only stops speech.",
        ),
        (
            "sendText(text)  [async]",
            """async function sendText(text) {
  addBubble("user", text, "You");
  history.push({ role: "user", content: text });
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, language, history }),
  });
  const data = await res.json();
  addBubble("bot", data.reply, "Lentswe");
  await maybeSpeak(speakable(data.reply), data.language);
}""",
            "Same idea as sendAudio but for typing and greeting chips. POST /api/chat with JSON. language comes from the dropdown (or auto).",
        ),
        (
            "maybeSpeak(text, language)  [async]",
            """async function maybeSpeak(text, language) {
  const res = await fetch("/api/speak", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, language }),
  });
  const type = res.headers.get("content-type") || "";
  if (!type.includes("audio")) return;
  const blob = await res.blob();
  await playBlob(blob);
}""",
            "Asks Python to turn text into sound. If the response is not audio (no voice for that language), it returns and the user only sees text.",
        ),
        (
            "speakable(text)",
            """function speakable(text) {
  const first = (text || "").trim().split(/\\s+/)[0].replace(/[.,!?]/g, "");
  const words = ["Hello", "Hallo", "Molo", "Sawubona", "Dumela", ...];
  return words.find((w) => w.toLowerCase() === first.toLowerCase()) || text;
}""",
            "If the reply starts with a native greeting word, speak only that short word (clearer TTS). Otherwise speak the full reply.",
        ),
        (
            "stopSpeech()",
            """function stopSpeech() {
  if (!currentAudio) return;
  currentAudio.pause();
  currentAudio.src = "";
  currentAudio = null;
  if (stopSpeechBtn) stopSpeechBtn.hidden = true;
}""",
            "Stops the playing reply and hides the Hush button.",
        ),
        (
            "playBlob(blob)",
            """function playBlob(blob) {
  stopSpeech();
  return new Promise((resolve) => {
    const audio = new Audio(URL.createObjectURL(blob));
    currentAudio = audio;
    stopSpeechBtn.hidden = false;
    audio.onended = () => { /* hide hush */ resolve(); };
    audio.play();
  });
}""",
            "Plays the MP3/WAV from the server. Promise lets sendText wait until speech finishes (needed for Play all 11).",
        ),
        (
            "renderGreetingChips()",
            """function renderGreetingChips() {
  const wrap = document.getElementById("greet-chips");
  for (const item of JABU_GREETINGS) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.innerHTML = `<span class="word">${item.word}</span>...`;
    btn.addEventListener("click", () => {
      languageSelect.value = item.lang;
      sendText(item.say);
    });
    wrap.appendChild(btn);
  }
}""",
            "Builds the 11 greeting buttons. Click sets the language and sendText with Sawubona / Dumela / etc.",
        ),
        (
            "startRecording()  [async]",
            """async function startRecording() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  recorder = new MediaRecorder(stream);
  recorder.ondataavailable = (event) => chunks.push(event.data);
  recorder.onstop = async () => { await sendAudio(blob); };
  recorder.start();
  recording = true;
  micButton.classList.add("hot");
}""",
            "Asks for the microphone. Starts MediaRecorder. On stop, sendAudio. class hot is the pink listening style.",
        ),
        (
            "stopRecording()",
            """function stopRecording() {
  if (!recording || !recorder) return;
  recording = false;
  micButton.classList.remove("hot");
  recorder.stop();
}""",
            "Stops the recorder. That fires onstop, which sends the audio.",
        ),
        (
            "writeString(offset, str)  [inside encodeWav]",
            """function writeString(offset, str) {
  for (let i = 0; i < str.length; i += 1)
    view.setUint8(offset + i, str.charCodeAt(i));
}""",
            "Helper: writes ASCII letters (RIFF, WAVE, fmt, data) into the WAV header bytes.",
        ),
    ]

    story.append(P("6. Every JavaScript function", st["h1"]))
    story.append(P("For each one: write the name, the short code, then the explanation in your own words.", st["note"]))

    for name, snippet, why in funcs:
        story.append(P(name, st["h2"]))
        story.append(code_block(snippet, st["code"]))
        story.append(P("<b>Explanation:</b> " + why, st["body"]))

    story.append(P("7. Event listeners (not named functions, still learn them)", st["h1"]))
    story.append(code_block(
        """micButton.addEventListener("click", ...);
  // if recording: stopRecording(); else startRecording();

form.addEventListener("submit", ...);
  // preventDefault so the page does not reload
  // sendText(textInput.value)

languageSelect.addEventListener("change", updateSpokenHint);

stopSpeechBtn.addEventListener("click", stopSpeech);

play-all click: loop JABU_GREETINGS and await sendText each one

loadLanguages().then(() => renderGreetingChips());""",
        st["code"],
    ))
    story.append(P(
        "preventDefault() on the form is important. Without it, Send reloads the page and the chat disappears.",
        st["body"],
    ))

    story.append(P("8. Python functions (backend — short list to write down)", st["h1"]))
    story.append(P(
        "You do not need PHP. Flask routes in app.py call these.",
        st["body"],
    ))
    py = [
        ("app.py home()", "Sends index.html."),
        ("app.py languages()", "JSON list of 11 languages."),
        ("app.py talk()", "Receives WAV, transcribe_wav, think, returns transcript + reply."),
        ("app.py chat()", "Receives JSON text, think, returns reply."),
        ("app.py speak_route()", "speak() TTS bytes, or skipped if no voice."),
        ("stt.transcribe_wav()", "Google STT. Returns (text, language_id)."),
        ("brain.think()", "Wake word, weather, search, stop, or chat.reply."),
        ("intents.local_reply()", "Greetings, who are you, time, help — no API key."),
        ("chat.reply()", "local_reply first, else OpenAI if a key exists."),
        ("tts.speak()", "edge-tts / gTTS / OpenAI speech → audio bytes."),
        ("weather.forecast()", "Open-Meteo for a city in the sentence."),
        ("web_search.search()", "Looks up a query."),
        ("wake_word.strip_wake()", "Removes hey Lentswe from the start."),
        ("languages.public_language_list()", "id, name, native, spoken flag."),
    ]
    prow = [[P("<b>Function</b>", st["body"]), P("<b>Explanation</b>", st["body"])]]
    for n, w in py:
        prow.append([P(f"<font face='Courier'>{n}</font>", st["body"]), P(w, st["body"])])
    t3 = Table(prow, colWidths=[55 * mm, 125 * mm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#e4ece6")),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t3)

    story.append(P("9. What to write in your notebook (order)", st["h1"]))
    story.append(P(
        "1. The three file names and what each does.<br/>"
        "2. The id table.<br/>"
        "3. The :root CSS block.<br/>"
        "4. Function names + one sentence each (section 6).<br/>"
        "5. Flow: mic click → startRecording → stopRecording → sendAudio → /api/talk → addBubble → maybeSpeak.<br/>"
        "6. Flow: type Send → sendText → /api/chat → addBubble → maybeSpeak.",
        st["body"],
    ))

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="Lentswe UI Study Notes",
        author="Lentswe voice assistant",
    )
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    build()
