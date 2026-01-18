"""
tts_english_offline.py
-------------------------------------------------
English Offline Text-to-Speech Engine
"""

import pyttsx3
import os
import time
import threading
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


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

        output_dir = os.path.dirname(wav_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        print(f"Saving to WAV: {wav_path}")
        self.engine.save_to_file(text, wav_path)
        self.engine.runAndWait()
        
        # Verify file was created
        if not os.path.exists(wav_path):
            raise Exception(f"WAV file was not created at {wav_path}")
        
        return wav_path

    def save_to_mp3(self, text: str, mp3_path: str):
        """
        Save speech to MP3 format (via WAV conversion)
        """
        if not PYDUB_AVAILABLE:
            # Fallback to WAV if pydub not available
            wav_path = mp3_path.replace(".mp3", ".wav")
            return self.save_to_wav(text, wav_path)
            
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
    gender: str = "female",
    max_retries: int = 2
):
    """
    English TTS with improved error handling and retry logic
    """
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty")
    
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    last_error = None
    
    for attempt in range(max_retries):
        engine = None
        wav_file = None
        
        try:
            # Initialize engine with error handling
            import pyttsx3
            engine = pyttsx3.init()
            
            if not engine:
                raise Exception("Failed to initialize TTS engine")
            
            # Configure engine settings
            engine.setProperty("rate", 180)
            engine.setProperty("volume", 1.0)
            
            # Set voice with fallback
            voices = engine.getProperty("voices")
            if voices and len(voices) > 0:
                # Try to find English voice
                english_voice = None
                for voice in voices:
                    if voice and hasattr(voice, 'languages'):
                        if 'en' in str(voice.languages).lower():
                            english_voice = voice
                            break
                
                if english_voice:
                    engine.setProperty("voice", english_voice.id)
                else:
                    engine.setProperty("voice", voices[0].id)
            
            # Determine output file path
            if output_file.endswith(".mp3"):
                wav_file = output_file.replace(".mp3", ".wav")
            else:
                wav_file = output_file
            
            # Generate audio with timeout protection
            import threading
            import time
            
            generation_complete = threading.Event()
            generation_error = None
            
            def generate_audio():
                nonlocal generation_error
                try:
                    engine.save_to_file(text, wav_file)
                    engine.runAndWait()
                    generation_complete.set()
                except Exception as e:
                    generation_error = e
                    generation_complete.set()
            
            # Start generation in separate thread
            thread = threading.Thread(target=generate_audio)
            thread.daemon = True
            thread.start()
            
            # Wait with timeout (30 seconds)
            if not generation_complete.wait(timeout=30):
                raise Exception("TTS generation timeout")
            
            if generation_error:
                raise generation_error
            
            # Validate generated file
            if not os.path.exists(wav_file):
                raise Exception(f"Audio file not created at {wav_file}")
            
            file_size = os.path.getsize(wav_file)
            if file_size == 0:
                raise Exception("Generated audio file is empty")
            
            if file_size < 1000:  # Less than 1KB might indicate issues
                raise Exception("Generated audio file too small")
            
            return wav_file
            
        except Exception as e:
            last_error = e
            
            # Clean up failed attempt
            if wav_file and os.path.exists(wav_file):
                try:
                    os.remove(wav_file)
                except:
                    pass
            
            # Clean up engine
            if engine:
                try:
                    engine.stop()
                except:
                    pass
            
            # Wait before retry
            if attempt < max_retries - 1:
                time.sleep(1)
    
    # All retries failed
    raise Exception(f"Offline TTS failed after {max_retries} attempts: {str(last_error)}")
