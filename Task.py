"""Skill actions: time/date/day + wikipedia / youtube / google."""
import datetime
from Speak import Say


def Time():
    Say(datetime.datetime.now().strftime("%H:%M"))


def Date():
    # FIX (was Say(date_obj) — TTS needs a string):
    Say(str(datetime.date.today()))


def Day():
    Say(datetime.datetime.now().strftime("%A"))


def NonInputExecution(query: str):
    query = str(query).lower()
    if "time" in query:
        Time()
    elif "date" in query:
        Date()
    elif "day" in query:
        Day()
    else:
        Say(query)


def _clean_topic(query: str) -> str:
    q = str(query).lower()
    for token in ("who is", "what is", "about", "wikipedia", "tell me"):
        q = q.replace(token, "")
    return q.strip(" ?.") or str(query).strip()


def InputExecution(tag: str, query: str):
    tag = str(tag).lower()

    if "play" in tag:
        song = str(query).lower().replace("play", "").strip()
        if not song:
            Say("What should I play?")
            return
        Say("Playing " + song)  # FIX (was 'playing'+song — missing space)
        try:
            import pywhatkit
            pywhatkit.playonyt(song)
        except Exception as e:
            Say(f"Could not play on YouTube: {e}")

    elif "wikipedia" in tag:
        # FIX (was double-summary: summary(query) then summary(summary) → PageError):
        topic = _clean_topic(query)
        Say("Searching Wikipedia for " + topic)
        try:
            import wikipedia
            Say(wikipedia.summary(topic, sentences=2))
        except Exception as e:
            Say(f"Wikipedia lookup failed: {e}")

    elif "google" in tag:
        q = str(query).lower().replace("google", "").replace("search", "").strip()
        if not q:
            Say("What should I search for?")
            return
        Say("Searching Google for " + q)
        try:
            import pywhatkit
            pywhatkit.search(q)
        except Exception as e:
            Say(f"Google search failed: {e}")

    else:
        Say(f"No action defined for {tag}")
