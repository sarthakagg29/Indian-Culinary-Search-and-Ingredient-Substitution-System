# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120

"""Cleans a name or a search query so two spellings can be compared."""
import re
import unicodedata

NUKTA = "़"            # the dot under a letter: ज़ and ज count as the same
CHANDRABINDU = "ँ"     # ँ  (written the same as the anusvara ं by many people)
ANUSVARA = "ं"
ZERO_WIDTH = ("​", "‌", "‍")


def is_devanagari(text):
    """True if the text has at least one Hindi (Devanagari) letter."""
    return any("ऀ" <= ch <= "ॿ" for ch in text)
     

def normalize(text):
    """Lowercase, remove the nukta, turn punctuation into spaces, squeeze extra spaces."""
    text = unicodedata.normalize("NFC", text or "").lower()
    for mark in ZERO_WIDTH:
        text = text.replace(mark, "")
    text = text.replace(NUKTA, "").replace(CHANDRABINDU, ANUSVARA)
    # keep letters, digits, spaces and Hindi vowel signs; everything else becomes a space
    text = re.sub(r"[^\w\sऀ-ॣ०-ॿ]|_", " ", text)
    return re.sub(r"\s+", " ", text).strip()
