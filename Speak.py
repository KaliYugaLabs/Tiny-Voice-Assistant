"""Text-to-speech. Singleton engine, cross-platform, never crashes the app."""
import pyttsx3

_engine = None


def _get_engine():
    global _engine
    if _engine is not None:
        return _engine
    # FIX (was init("sapi5") — Windows-only, crashes on Linux/Mac):
    try:
        _engine = pyttsx3.init("sapi5")
    except Exception:
        _engine = pyttsx3.init()
    try:
        voices = _engine.getProperty("voices")
        if voices:
            # FIX (was setProperty('voices', ...) — correct key is 'voice' singular):
            _engine.setProperty("voice", voices[0].id)
        _engine.setProperty("rate", 170)
    except Exception:
        pass
    return _engine


def Say(text) -> None:
    text = str(text)  # FIX: Date()/Time() passed non-string objects
    print(f"\nNirav: {text}\n")
    try:
        engine = _get_engine()
        engine.say(text)  # positional — widest version compatibility
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS unavailable: {e}]")
