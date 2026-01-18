from flask import Flask, request, jsonify, send_file, render_template, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
import tempfile
from langdetect import detect, DetectorFactory
from tts_english_online import english_online_tts
from english_offline_tts import generate_english_offline_tts
from tts_urdu import generate_urdu_tts
from text_extractor import extract_text_from_file, get_supported_extensions

DetectorFactory.seed = 0

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:5000", "http://localhost:5000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = get_supported_extensions()
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (increased for document files)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_content(filepath):
    """Basic file validation without magic library"""
    try:
        # Basic file size and existence check
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            return False
        return True
    except:
        return False

def get_extraction_method(file_extension):
    """Return the extraction method used for each file type"""
    methods = {
        '.txt': 'Direct text reading',
        '.pdf': 'PDF text extraction',
        '.docx': 'Word document parsing',
        '.doc': 'Legacy Word document parsing',
        '.pptx': 'PowerPoint slide parsing',
        '.jpg': 'OCR (Optical Character Recognition)',
        '.jpeg': 'OCR (Optical Character Recognition)',
        '.png': 'OCR (Optical Character Recognition)'
    }
    return methods.get(file_extension.lower(), 'Unknown')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/test-tts', methods=['GET'])
def test_tts():
    """Simple test endpoint for TTS"""
    try:
        test_text = "Hello, this is a test."
        unique_id = uuid.uuid4().hex[:8]
        
        # Test English online TTS
        audio_path = english_online_tts(test_text, OUTPUT_FOLDER)
        
        if audio_path and os.path.exists(audio_path):
            return jsonify({
                'success': True, 
                'message': 'TTS test successful',
                'file_path': audio_path,
                'file_size': os.path.getsize(audio_path)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'TTS test failed - no audio file generated',
                'file_path': audio_path
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'TTS test error: {str(e)}'
        })

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'Invalid file type'}), 400
        
        filename = secure_filename(file.filename)
        file_extension = os.path.splitext(filename)[1].lower()
        filepath = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}_{filename}")
        
        file.save(filepath)
        
        if not validate_file_content(filepath):
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': 'Invalid file content'}), 400
        
        try:
            text = extract_text_from_file(filepath, file_extension)
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Text extraction failed: {str(e)}'}), 500
        
        if os.path.exists(filepath):
            os.remove(filepath)
        
        if not text or not text.strip():
            return jsonify({'error': 'No text extracted'}), 400
        
        return jsonify({
            'text': text.strip(),
            'success': True,
            'file_type': file_extension,
            'extraction_method': get_extraction_method(file_extension)
        })
    
    except Exception as e:
        if 'filepath' in locals() and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/detect-language', methods=['POST'])
def detect_language():
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        lang = detect(text)
        confidence = min(0.95, 0.70 + (min(len(text), 1000) / 1000) * 0.25)
        
        lang_map = {'en': 'English', 'ur': 'Urdu', 'hi': 'Hindi', 'ar': 'Arabic'}
        
        if lang in ['hi', 'ar'] and any(char in text for char in 'ابتثجحخدذرزسشصضطظعغفقکگلمنوہی'):
            lang = 'ur'
        
        if lang not in ['en', 'ur']:
            lang = 'en'
            confidence = 0.60
        
        return jsonify({
            'language': lang,
            'language_name': lang_map.get(lang, 'English'),
            'confidence': confidence,
            'supported': True
        })
    
    except Exception as e:
        return jsonify({
            'language': 'en',
            'language_name': 'English',
            'confidence': 0.50,
            'supported': True
        })

@app.route('/tts', methods=['POST'])
def text_to_speech():
    data = request.get_json()
    text = data.get('text', '').strip()
    language = data.get('language', 'en')
    mode = data.get('mode', 'online')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    if len(text) > 5000:
        return jsonify({'error': 'Text too long. Maximum 5000 characters allowed.'}), 400
    
    audio_path = None
    fallback_attempted = False
    
    try:
        unique_id = uuid.uuid4().hex[:8]
        
        # TTS generation with fallback handling
        if language == 'ur':
            if mode == 'online':
                temp_file = os.path.join(OUTPUT_FOLDER, f"urdu_online_{unique_id}.mp3")
                try:
                    audio_path = generate_urdu_tts(text, mode, temp_file)
                except Exception as e:
                    # Fallback to offline for Urdu
                    fallback_attempted = True
                    temp_file = os.path.join(OUTPUT_FOLDER, f"urdu_offline_{unique_id}.wav")
                    audio_path = generate_urdu_tts(text, 'offline', temp_file)
            else:
                temp_file = os.path.join(OUTPUT_FOLDER, f"urdu_offline_{unique_id}.wav")
                audio_path = generate_urdu_tts(text, mode, temp_file)
        else:
            if mode == 'online':
                try:
                    audio_path = english_online_tts(text, OUTPUT_FOLDER)
                except Exception as e:
                    # Fallback to offline for English
                    fallback_attempted = True
                    temp_file = os.path.join(OUTPUT_FOLDER, f"english_offline_{unique_id}.wav")
                    audio_path = generate_english_offline_tts(text, temp_file)
            else:
                temp_file = os.path.join(OUTPUT_FOLDER, f"english_offline_{unique_id}.wav")
                audio_path = generate_english_offline_tts(text, temp_file)
        
        # Validate audio file
        if not audio_path or not os.path.exists(audio_path):
            raise Exception('Audio file not generated')
        
        file_size = os.path.getsize(audio_path)
        if file_size == 0:
            raise Exception('Generated audio file is empty')
        
        if file_size < 1000:  # Less than 1KB might indicate corruption
            raise Exception('Generated audio file appears corrupted')
        
        # Secure file streaming with error handling
        def generate_audio():
            try:
                with open(audio_path, 'rb') as f:
                    chunk_size = 8192
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
            except Exception as e:
                # If streaming fails, yield error indicator
                yield b''
            finally:
                # Clean up after streaming
                try:
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                except:
                    pass
        
        # Determine MIME type and headers
        if audio_path.endswith('.wav'):
            mimetype = 'audio/wav'
            file_ext = 'wav'
        else:
            mimetype = 'audio/mpeg'
            file_ext = 'mp3'
        
        headers = {
            'Content-Disposition': f'inline; filename="speech_{language}_{unique_id}.{file_ext}"',
            'Content-Length': str(file_size),
            'Accept-Ranges': 'bytes',
            'Cache-Control': 'no-cache'
        }
        
        if fallback_attempted:
            headers['X-Fallback-Used'] = 'true'
        
        return Response(
            generate_audio(),
            mimetype=mimetype,
            headers=headers
        )
    
    except Exception as e:
        # Clean up on error
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass
        
        error_msg = f'TTS failed: {str(e)}'
        if fallback_attempted:
            error_msg += ' (fallback also failed)'
        
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)
