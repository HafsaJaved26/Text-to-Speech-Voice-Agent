"""
English Online Text-to-Speech Module
Technology: gTTS (Google Text-to-Speech)
"""

import os
import hashlib
from gtts import gTTS

# Directory to store cached audio files
CACHE_DIR = "tts_cache_english"
os.makedirs(CACHE_DIR, exist_ok=True)

def _generate_cache_key(text: str) -> str:
    """
    Generates a unique hash key for caching TTS responses
    """
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def english_online_tts(
    text: str,
    output_dir: str = "output_audio",
    slow: bool = False,
    bitrate: str = "192k"
) -> str:
    """
    Converts English text to speech using Google TTS (Online)
    """

    if not text.strip():
        raise ValueError("Input text cannot be empty")

    os.makedirs(output_dir, exist_ok=True)

    cache_key = _generate_cache_key(text)
    # Check global cache first
    cached_file = os.path.join(CACHE_DIR, f"{cache_key}.mp3")
    
    if os.path.exists(cached_file):
        return cached_file

    # Generate TTS
    tts = gTTS(
        text=text,
        lang="en",
        slow=slow
    )

    output_path = os.path.join(output_dir, f"{cache_key}.mp3")
    tts.save(output_path)

    # Save copy to cache
    os.replace(output_path, cached_file)

    return cached_file