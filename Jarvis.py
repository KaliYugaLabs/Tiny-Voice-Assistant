"""Jarvis — voice/text assistant. Run: python Jarvis.py [--text]"""
import json
import random
import sys

import torch

from Brain import NeuralNet
from NeuralNetwork import bag_of_words, tokenize

BOTNAME = "Nirav"
CONFIDENCE_THRESHOLD = 0.75

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

with open("intents.json", "r") as json_data:
    intents = json.load(json_data)

FILE = "TrainData.pth"
# FIX (was torch.load(FILE) — crashes when trained on GPU, run on CPU):
data = torch.load(FILE, map_location=device, weights_only=False)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

from Speak import Say
from Task import InputExecution, NonInputExecution


def predict(sentence: str):
    """Return (tag, confidence) — testable without a microphone."""
    tokens = tokenize(sentence)
    X = bag_of_words(tokens, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)
    with torch.no_grad():
        output = model(X)
        _, predicted = torch.max(output, dim=1)
        tag = tags[predicted.item()]
        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()].item()
    return tag, prob


def handle(sentence: str) -> bool:
    """Process one utterance. Returns False to quit, True to continue."""
    sentence = (sentence or "").strip().lower()
    if not sentence:
        Say("I didn't catch that. Could you repeat?")
        return True
    if sentence in ("bye", "goodbye", "exit", "quit", "sleep"):
        Say("Goodbye. See you later.")
        return False
    # FIX (was `if stop: Main()` — infinite recursion): just acknowledge & continue
    if sentence == "stop":
        Say("Okay, stopped. Anything else?")
        return True

    tag, prob = predict(sentence)

    if prob > CONFIDENCE_THRESHOLD:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                reply = random.choice(intent["responses"])
                low = reply.lower()
                if "time" in low or "date" in low or "day" in low:
                    NonInputExecution(reply)
                elif "wikipedia" in low or "google" in low or "play" in low:
                    InputExecution(reply, sentence)
                else:
                    Say(reply)
                break
    else:
        # FIX (was silent on low confidence — now always answers):
        Say("I'm not sure I understood. Could you rephrase?")
    return True


def get_input(text_mode: bool) -> str:
    if text_mode:
        try:
            return input("You: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return "bye"
    try:
        from Listen import Listen
        heard = Listen()
        if heard:
            return heard
        # Mic empty/failed → fall back to keyboard so the app never dead-loops
        print("(mic heard nothing — type instead, or 'bye' to quit)")
        try:
            return input("You: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return "bye"
    except Exception as e:
        print(f"Mic unavailable ({e}) — typing mode.")
        try:
            return input("You: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return "bye"


def main():
    text_mode = "--text" in sys.argv
    print(f"{BOTNAME} ready. Talk or type. Say 'bye' to quit. (hint: python Jarvis.py --text)")
    running = True
    while running:
        running = handle(get_input(text_mode))


if __name__ == "__main__":
    main()
