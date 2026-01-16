import os
import uuid
import shutil
from google.colab import files

from combined_module_01 import extract_text
from module2_py import TextProcessor
from english_offline_tts import generate_english_offline_tts
from tts_urdu import generate_urdu_tts

from tts_english_online import english_online_tts

class PipelineManager:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self.processor = TextProcessor()
        os.makedirs(self.output_dir, exist_ok=True)

    def process_request(self, file_path, mode="online"):
        print(f"\n🚀 [Manager] Starting Pipeline for: {file_path}")

        print("   └── [Step 1] Extracting text...")
        try:
            raw_text = extract_text(file_path)
            if not raw_text or len(raw_text) < 2:
                print("❌ Error: Text extraction returned empty.")
                return None
        except Exception as e:
            print(f"❌ Critical Error in Extraction: {e}")
            return None

        print("   └── [Step 2] Cleaning & Detecting Language...")
        clean_text = self.processor.clean_text(raw_text)
        prep_result = self.processor.prepare_text_for_tts(clean_text)
        final_text = prep_result["text"]
        language = prep_result["language"]

        print(f"       ├── Detected Language: {language.upper()}")
        print(f"       ├── Text Snippet: {final_text[:50]}...")

        print(f"   └── [Step 3] Generating Audio ({mode})...")

        unique_id = str(uuid.uuid4())[:8]
        std_output_file = f"{self.output_dir}/speech_{language}_{unique_id}.mp3"

        audio_path = None

        try:
            if language == 'ur':
                audio_path = generate_urdu_tts(final_text, mode, std_output_file)

            elif language == 'en':
                if mode == "online":
                    audio_path = english_online_tts(
                        text=final_text,
                        output_dir=self.output_dir
                    )
                else:
                    audio_path = generate_english_offline_tts(final_text, std_output_file)
            else:
                print(f"❌ Error: Unsupported Language '{language}'")
                return None

        except Exception as e:
            print(f"❌ Error in TTS Generation: {e}")
            return None

        if audio_path:
            print(f"✅ DONE! Audio saved: {audio_path}")
            return audio_path
        else:
            print("❌ TTS Engine returned None.")
            return None

if __name__ == "__main__":
    manager = PipelineManager()

    print("=== 🎤 TEAM TTS: INTEGRATED PIPELINE ===")
    print("👇 Click below to upload your file (PDF, DOCX, or Image)")

    uploaded = files.upload()

    mode = input("⚙️  Select Mode (online/offline): ").strip().lower()
    if mode not in ['online', 'offline']:
        mode = 'online'

    for filename in uploaded.keys():
        result_path = manager.process_request(filename, mode)

        if result_path:
            print(f"\n🎧 Playing Audio for {filename}:")
            try:
                from IPython.display import Audio, display
                display(Audio(result_path))
            except:
                pass