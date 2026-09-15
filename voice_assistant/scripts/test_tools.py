from src.brain import think

h = []
checks = [
    "hello lentswe",
    "call for help",
    "add to my list buy bread",
    "what's on my list",
    "mark buy bread as done",
    "my goal is save 500 this month",
    "how am I doing on my goals",
    "log that I have a headache",
    "show my symptoms",
]
for msg in checks:
    out = think(msg, "english", h)
    print(msg, "=>", (out or "")[:90].replace("\n", " "))
