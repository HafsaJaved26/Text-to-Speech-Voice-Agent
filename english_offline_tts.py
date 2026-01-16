"""
tts_english_offline.py
-------------------------------------------------
English Offline Text-to-Speech Engine
"""

import pyttsx3
import os
from pydub import AudioSegment


class EnglishOfflineTTS:
    def __init__(
        self,
        rate: int = 155,
        volume: float = 1.0,
        accent: str = "us",
        gender: str = "female"
    ):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        self._set_voice(accent, gender)

    def _set_voice(self, accent: str, gender: str):
        """
        Select best available English voice
        Priority:
        1. Accent + Gender
        2. Accent only
        3. Any English voice
        4. System fallback
        """
        voices = self.engine.getProperty("voices")

        def is_english(v):
            return "en" in str(v.languages).lower() or "english" in v.name.lower()

        def match_accent(v):
            text = (v.name + str(v.languages)).lower()
            if accent == "us":
                return "us" in text or "united states" in text
            if accent == "uk":
                return "uk" in text or "united kingdom" in text
            return False

        def match_gender(v):
            name = v.name.lower()
            if gender == "female":
                return any(x in name for x in ["female", "zira", "susan"])
            if gender == "male":
                return any(x in name for x in ["male", "david", "mark"])
            return False

        # 1️⃣ Accent + Gender
        for v in voices:
            if is_english(v) and match_accent(v) and match_gender(v):
                self.engine.setProperty("voice", v.id)
                return

        # 2️⃣ Accent only
        for v in voices:
            if is_english(v) and match_accent(v):
                self.engine.setProperty("voice", v.id)
                return

        # 3️⃣ Any English
        for v in voices:
            if is_english(v):
                self.engine.setProperty("voice", v.id)
                return

        # 4️⃣ Fallback
        self.engine.setProperty("voice", voices[0].id)

    def speak(self, text: str):
        """
        Speak text in real-time (no file saved)
        """
        if not text or not text.strip():
            raise ValueError("Text is empty")

        self.engine.say(text)
        self.engine.runAndWait()

    def save_to_wav(self, text: str, wav_path: str):
        """
        Save speech to WAV format
        """
        if not text or not text.strip():
            raise ValueError("Text is empty")

        os.makedirs(os.path.dirname(wav_path), exist_ok=True)
        self.engine.save_to_file(text, wav_path)
        self.engine.runAndWait()
        return wav_path

    def save_to_mp3(self, text: str, mp3_path: str):
        """
        Save speech to MP3 format (via WAV conversion)
        """
        wav_temp = mp3_path.replace(".mp3", ".wav")
        self.save_to_wav(text, wav_temp)

        audio = AudioSegment.from_wav(wav_temp)
        audio.export(mp3_path, format="mp3")
        os.remove(wav_temp)

        return mp3_path


# ---------- Integration-Friendly Function ----------

def generate_english_offline_tts(
    text: str,
    output_file: str = "output/english_offline.mp3",
    accent: str = "us",
    gender: str = "female"
):
    """
    One-call TTS generator for offline English
    """
    tts = EnglishOfflineTTS(accent=accent, gender=gender)

    if output_file.endswith(".mp3"):
        return tts.save_to_mp3(text, output_file)
    return tts.save_to_wav(text, output_file)