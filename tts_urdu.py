import os
import subprocess
from gtts import gTTS

class UrduTTS:
    def __init__(self):
        pass

    def speak_online(self, text: str, output_file: str = "output/urdu_online.mp3"):
        """
        High-quality Urdu TTS using Google TTS (Requires Internet).
        """
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            tts = gTTS(text=text, lang='ur', slow=False)
            tts.save(output_file)
            return output_file
        except Exception as e:
            print(f"❌ Error in Urdu Online TTS: {e}")
            return None

    def speak_offline(self, text: str, output_file: str = "output/urdu_offline.wav"):
        """
        Offline Urdu TTS using direct eSpeak-ng command.
        Strictly enforces Urdu language (-v ur).
        """
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Ensure output ends in .wav for eSpeak
            if output_file.endswith(".mp3"):
                output_file = output_file.replace(".mp3", ".wav")

            # Command: espeak-ng -v ur -w output.wav "Text"
            # -v ur : Urdu language
            # -s 140 : Speed (words per minute)
            command = ["espeak-ng", "-v", "ur", "-s", "140", "-w", output_file, text]
            
            subprocess.run(command, check=True)
            return output_file
            
        except Exception as e:
            print(f"❌ Error in Urdu Offline TTS (eSpeak-ng): {e}")
            print("💡 Tip: Make sure 'espeak-ng' is installed (!apt-get install espeak-ng)")
            return None

# Wrapper function for integration
def generate_urdu_tts(text: str, mode: str = "online", output_file: str = "output/urdu.mp3"):
    engine = UrduTTS()
    if mode == "online":
        return engine.speak_online(text, output_file)
    else:
        return engine.speak_offline(text, output_file)