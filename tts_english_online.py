"""
English Online Text-to-Speech Module
Technology: gTTS (Google Text-to-Speech)
"""

import os
import hashlib
from gtts import gTTS
import threading
import time
import requests

CACHE_DIR = "tts_cache_english"
os.makedirs(CACHE_DIR, exist_ok=True)

cache_lock = threading.Lock()

def _generate_cache_key(text: str) -> str:
    """
    Generates a unique hash key for caching TTS responses
    """
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def _check_internet_connection(timeout=5):
    """Check if internet connection is available"""
    try:
        response = requests.get('https://www.google.com', timeout=timeout)
        return response.status_code == 200
    except:
        return False

def english_online_tts(
    text: str,
    output_dir: str = "output_audio",
    slow: bool = False,
    bitrate: str = "192k",
    max_retries: int = 3,
    timeout: int = 30
) -> str:
    if not text.strip():
        raise ValueError("Input text cannot be empty")

    os.makedirs(output_dir, exist_ok=True)
    cache_key = _generate_cache_key(text)
    output_path = os.path.join(output_dir, f"english_online_{cache_key}.mp3")
    cached_file = os.path.join(CACHE_DIR, f"{cache_key}.mp3")
    
    # Check cache first (faster)
    with cache_lock:
        if os.path.exists(cached_file) and os.path.getsize(cached_file) > 0:
            import shutil
            shutil.copy2(cached_file, output_path)
            return output_path

    # Check internet connection
    if not _check_internet_connection():
        raise Exception("No internet connection available for online TTS")

    last_error = None
    for attempt in range(max_retries):
        try:
            # Optimized gTTS settings with timeout handling
            tts = gTTS(text=text, lang="en", slow=slow, tld='com')
            
            # Set timeout for the save operation
            start_time = time.time()
            tts.save(output_path)
            
            # Check if operation took too long
            if time.time() - start_time > timeout:
                raise Exception("TTS generation timeout")
            
            # Validate generated file
            if not os.path.exists(output_path):
                raise Exception("Audio file not created")
            
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                raise Exception("Generated audio file is empty")
            
            if file_size < 500:  # Less than 500 bytes might indicate error
                raise Exception("Generated audio file too small, likely corrupted")
            
            # Cache for future use
            with cache_lock:
                try:
                    import shutil
                    shutil.copy2(output_path, cached_file)
                except:
                    pass

            return output_path
            
        except Exception as e:
            last_error = e
            
            # Clean up failed attempt
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 1  # 1, 2, 4 seconds
                time.sleep(wait_time)
    
    # All retries failed
    raise Exception(f"TTS failed after {max_retries} attempts: {str(last_error)}")