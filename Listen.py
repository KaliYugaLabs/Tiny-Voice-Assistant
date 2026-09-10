"""Microphone input. Returns lowercase text, or "" on failure (never crashes)."""
import speech_recognition as sr


def Listen(timeout: int = 5, phrase_time_limit: int = 5) -> str:
    r = sr.Recognizer()
    try:
        mic = sr.Microphone()
    except OSError:
        print("Microphone not found — use typed input instead.")
        return ""

    with mic as source:
        print("Listening...")
        # FIX (was after listen): calibrate BEFORE capturing
        r.adjust_for_ambient_noise(source, duration=0.5)
        r.pause_threshold = 1
        try:
            # FIX (was listen(source, 0, 4) — timeout=0 misbehaves):
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return ""

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print(f"You Said: {query}")
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"Speech service unavailable: {e}")
        return ""
    except Exception as e:  # never let STT kill the assistant
        print(f"Listen error: {e}")
        return ""

    return str(query).lower()
