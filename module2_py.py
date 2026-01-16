import re
from langdetect import detect, LangDetectException

class TextProcessor:
    def __init__(self):
        pass

    # ---------- Cleaning ----------
    def clean_text(self, text):
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n+", "\n", text)
        return text.strip()

    # ---------- Sentence Split ----------
    def split_sentences(self, text):
        return re.split(r'(?<=[.!?])\s+', text)

    # ---------- Chunking ----------
    def chunk_text(self, text, chunk_size=500):
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    # ---------- Language Detection ----------
    def detect_language(self, text):
        try:
            return detect(text)
        except LangDetectException:
            return "en"

    # ---------- TTS Preparation ----------
    def prepare_text_for_tts(self, text):
        lang = self.detect_language(text)

        if lang == "ur":
            # Urdu specific normalization
            text = text.replace("۔", ".").replace("،", ",").replace("\n", " ")
        else:
            # English normalization
            text = text.replace("\n", " ")
            lang = "en"

        return {
            "language": lang,
            "text": text.strip()
        }
