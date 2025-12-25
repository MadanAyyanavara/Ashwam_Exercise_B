# lang_detect/rules.py

import re

# Small Hindi words written in Latin (Hinglish markers)
HI_LATIN_WORDS = {
    "aaj", "aj", "kal", "hai", "h", "nahi", "nhi", "yaar",
    "raat", "subah", "theek", "thik", "dard", "dimag",
    "mujhe", "muje", "badh", "gaya", "gayi", "ho",
    "raha", "rahi", "thakan", "thak", "bahut", "bhut",
    "nahi", "hai", "thi", "tha", "ko", "raat",
}

# Simple English common words / stopwords for this domain
EN_WORDS = {
    "today", "yesterday", "headache", "cramps", "stress",
    "meeting", "meetings", "work", "was", "is", "are",
    "feeling", "very", "tired", "pain", "bloated", "after",
    "dinner", "need", "book", "appointment", "period",
    "morning", "evening", "ok", "fine", "energy", "low",
    "late", "no", "back", "skip", "better", "gyno",
    "anxiety", "emotional", "stressed", "intense", "today",
    "felt", "again", "early",
}

# Regex to extract words with Latin and Devanagari letters
TOKEN_RE = re.compile(r"[A-Za-z\u0900-\u097F]+")

def tokenize(text: str):
    """
    Simple tokenizer: returns lowercase tokens that contain
    Latin or Devanagari letters.
    """
    return TOKEN_RE.findall(text.lower())
