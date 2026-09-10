# Tiny Voice Assistant (PyTorch)

A small on-device voice/text assistant: microphone → intent classifier → speech + actions. A 3-layer MLP (~6 KB) trained on ~40 patterns across 11 intents, running on CPU with no API keys.

> Scope note: this is an intent classifier with STT/TTS, not a self-aware system. No online learning, no emotion model, no autonomy. The roadmap below is working toward a genuinely self-improving loop.

## Quickstart

Requires Python 3.11 and a microphone (optional — text mode works without one).

```bash
python -m venv .venv && .venv/Scripts/activate      # Windows
# source .venv/bin/activate                          # Linux/Mac
pip install -r requirements.txt
python Train.py                                       # writes TrainData.pth
python Jarvis.py --text                               # keyboard mode (no mic needed)
python Jarvis.py                                      # voice mode
```

## How it works

```
Mic ──> Listen.py (Google STT, en-in) ──> tokenize → bag-of-words
                                             │
                    Brain.py (Linear  n→8→8→11) ◄── intents.json
                                             │  softmax, threshold 0.75
            ┌────────────────────────────────┴───────────────────┐
     Speak.py (pyttsx3 TTS)                        Task.py (time/date/day,
                                                  wikipedia, youtube, google)
```

`predict()` in `Jarvis.py` is importable without a microphone, so training and inference can be tested headlessly.

## Layout

| File | Role |
|---|---|
| `Jarvis.py` | Main loop, confidence gating, `predict()` / `handle()` |
| `Train.py` | Dataset build + training, saves `TrainData.pth` |
| `Brain.py` | `NeuralNet` — 3-layer MLP |
| `NeuralNetwork.py` | `tokenize` / `stem` / `bag_of_words` |
| `Listen.py` | Mic capture, returns `""` on failure |
| `Speak.py` | Singleton TTS engine, cross-platform |
| `Task.py` | Time/date/day + wikipedia/youtube/google actions |
| `intents.json` | 11 intents, ~40 patterns (EN + some HI transliteration) |

## Configuration

- `CONFIDENCE_THRESHOLD = 0.75` in `Jarvis.py` — below this the assistant asks for a rephrase instead of acting.
- Intents live in `intents.json` (`tag` / `patterns` / `responses`). Retrain after edits: `python Train.py`.
- TTS voice/rate in `Speak.py`; STT language (`en-in`) and timeouts in `Listen.py`.

## Troubleshooting

- `punkt` / `punkt_tab` missing: handled automatically (`nltk.download` on first run). Offline fallback is whitespace split.
- PyAudio install fails: voice mode needs it; use `python Jarvis.py --text` instead. On Windows, `pip install PyAudio` from this repo's venv is verified working.
- `torch.load` device errors: loads use `map_location` so GPU-trained checkpoints open on CPU.
- Wikipedia says "lookup failed": ambiguous or missing page — try a more specific topic.

## Roadmap (functional, not cosmetic)

1. Teach-loop — correct a misclassification once (`wrong, that was time`) and the model fine-tunes on-device in seconds.
2. Unknown-mining — rejected utterances logged for review and promotion into new intents.
3. Hinglish normalization — systematic handling of EN/HI code-mix (`samay`, `tareek`, `din`) for the tiny model.

## License

No license file yet — add one (MIT recommended) before accepting contributions.
