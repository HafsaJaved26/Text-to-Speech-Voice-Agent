import os
import wave
import time
import threading
from gtts import gTTS
import requests

def _is_audio_silent(wav_file, threshold=0.01):
    """Check if WAV file contains mostly silent audio"""
    try:
        with wave.open(wav_file, 'rb') as wav:
            frames = wav.readframes(wav.getnframes())
            non_zero_ratio = sum(1 for b in frames if b != 0) / len(frames)
            return non_zero_ratio < threshold
    except:
        return True

def _check_internet_connection(timeout=5):
    """Check if internet connection is available"""
    try:
        response = requests.get('https://www.google.com', timeout=timeout)
        return response.status_code == 200
    except:
        return False

def generate_urdu_tts(text: str, mode: str = "online", output_file: str = "output/urdu.mp3", max_retries: int = 2):
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty")
    
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            if mode == "online":
                # Check internet connection first
                if not _check_internet_connection():
                    raise Exception("No internet connection for online TTS")
                
                # Generate online TTS with timeout
                tts = gTTS(text=text, lang='ur', slow=False)
                
                start_time = time.time()
                tts.save(output_file)
                
                if time.time() - start_time > 30:  # 30 second timeout
                    raise Exception("TTS generation timeout")
                
            else:
                # Offline mode with improved error handling
                import pyttsx3
                engine = None
                
                try:
                    engine = pyttsx3.init()
                    if not engine:
                        raise Exception("Failed to initialize TTS engine")
                    
                    engine.setProperty("rate", 180)
                    engine.setProperty("volume", 1.0)
                    
                    voices = engine.getProperty("voices")
                    if voices and len(voices) > 0:
                        engine.setProperty("voice", voices[0].id)
                    
                    wav_file = output_file.replace(".mp3", ".wav") if output_file.endswith(".mp3") else output_file
                    
                    # Use threading for timeout protection
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
                    
                    thread = threading.Thread(target=generate_audio)
                    thread.daemon = True
                    thread.start()
                    
                    if not generation_complete.wait(timeout=30):
                        raise Exception("Offline TTS generation timeout")
                    
                    if generation_error:
                        raise generation_error
                    
                    # Validate offline result
                    if os.path.exists(wav_file) and os.path.getsize(wav_file) > 1000 and not _is_audio_silent(wav_file):
                        return wav_file
                    
                    # Fallback to online if offline fails
                    if os.path.exists(wav_file):
                        os.remove(wav_file)
                    
                    if not _check_internet_connection():
                        raise Exception("Offline TTS failed and no internet for fallback")
                    
                    mp3_file = output_file.replace(".wav", ".mp3") if output_file.endswith(".wav") else output_file
                    tts = gTTS(text=text, lang='ur', slow=False)
                    tts.save(mp3_file)
                    output_file = mp3_file
                    
                finally:
                    if engine:
                        try:
                            engine.stop()
                        except:
                            pass
            
            # Validate final output
            if not os.path.exists(output_file):
                raise Exception("Audio file not created")
            
            file_size = os.path.getsize(output_file)
            if file_size == 0:
                raise Exception("Generated audio file is empty")
            
            if file_size < 500:
                raise Exception("Generated audio file too small")
            
            return output_file
            
        except Exception as e:
            last_error = e
            
            # Clean up failed attempt
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except:
                    pass
            
            # Wait before retry
            if attempt < max_retries - 1:
                time.sleep(1)
    
    # All retries failed
    raise Exception(f"Urdu TTS failed after {max_retries} attempts: {str(last_error)}")