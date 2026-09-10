"""NLP helpers: tokenize / stem / bag-of-words."""
import numpy as np
import nltk
from nltk.stem.porter import PorterStemmer

Stemmer = PorterStemmer()


def _ensure_punkt():
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt", quiet=True)
    # Newer NLTK (>=3.8.2) also needs punkt_tab
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        try:
            nltk.download("punkt_tab", quiet=True)
        except Exception:
            pass


def tokenize(sentence: str):
    _ensure_punkt()
    try:
        return nltk.word_tokenize(sentence)
    except LookupError:
        # Offline fallback — crude but never crashes
        return sentence.split()


def stem(word: str):
    return Stemmer.stem(word.lower())


def bag_of_words(tokenized_sentence, words):
    sentence_word = [stem(word) for word in tokenized_sentence]
    bag = np.zeros(len(words), dtype=np.float32)
    for idx, w in enumerate(words):
        if w in sentence_word:
            bag[idx] = 1
    return bag
