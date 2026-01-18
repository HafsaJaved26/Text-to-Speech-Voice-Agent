# 🎙️ Text-to-Speech (TTS) Voice Agent

A multilingual Text-to-Speech Voice Agent designed to convert text from documents, images, and direct input into natural-sounding speech.
The system supports English (online & offline) and Urdu TTS, with automatic language detection, file handling, and a web-based interface for real-time interaction.

# 👥 Team Members & Contributions

This project was collaboratively developed by a team of dedicated members:

Hafsa Javed 
Abdul Jabbar 
Afia Noor
Eman Afzal
Eiman Zahra Awan
Muhammad Zaheer 
Faraz Khan 
Fiza Aslam 
Ghazal Hafeez 

##  Features

- **Multi-language Support**: English and Urdu text-to-speech conversion
- **Document Processing**: Extract text from PDFs, Word documents, and images
- **Dual Mode Operation**: Online (high quality) and offline (no internet required) TTS
- **Smart Language Detection**: Automatically detects input language
- **File Upload Support**: Drag-and-drop interface for easy file processing
- **Audio Caching**: Intelligent caching system for improved performance
- **Responsive UI**: Clean, modern web interface

##  Quick Start

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Text-to-Speech-Voice-Agent-module-3
   ```

2. **Set up virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run setup script** (Windows)
   ```bash
   setup.bat
   ```

5. **Start the application**
   ```bash
   # Using batch file (Windows)
   run_app.bat
   
   # Or directly
   python app.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:5000`

##  Usage Guide

### Text Input Method
1. Enter or paste text (up to 5,000 characters)
2. Select language (auto-detected)
3. Choose TTS mode (online/offline)
4. Click "Generate Speech"
5. Download the generated audio file

### File Upload Method
1. Drag and drop supported files or click to browse
2. Supported formats: PDF, DOCX, DOC, PPTX, JPG, JPEG, PNG, TXT
3. Text is automatically extracted and processed
4. Follow text input steps for speech generation

##  Project Structure

```
├── app.py                 # Main Flask application
├── text_extractor.py      # Document text extraction module
├── tts_english_online.py  # Online English TTS service
├── english_offline_tts.py # Offline English TTS service
├── tts_urdu.py           # Urdu TTS service
├── templates/
│   └── index.html        # Web interface
├── static/               # Static assets
├── uploads/              # Temporary file uploads
├── output/               # Generated audio files
├── tts_cache_english/    # Audio cache storage
├── requirements.txt      # Python dependencies
├── setup.bat            # Windows setup script
└── run_app.bat          # Windows run script
```

##  Development Setup

### Additional Requirements for Image Processing

**Windows:**
```bash
# Download and install Tesseract OCR
# https://github.com/tesseract-ocr/tesseract/releases
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### Development Mode
```bash
# Enable debug mode
set FLASK_DEBUG=true     # Windows
export FLASK_DEBUG=true  # Linux/Mac

python app.py
```

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main web interface |
| GET | `/health` | Health check |
| GET | `/test-tts` | TTS functionality test |
| POST | `/upload` | File upload and text extraction |
| POST | `/detect-language` | Language detection |
| POST | `/tts` | Text-to-speech conversion |

### TTS Request Format
```json
{
  "text": "Your text here",
  "language": "en",
  "mode": "online"
}
```

##  Technology Stack

- **Backend Framework**: Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **TTS Services**: 
  - Google Text-to-Speech (online)
  - pyttsx3 (offline)
- **Document Processing**: 
  - PyPDF2 (PDF)
  - python-docx (Word documents)
  - python-pptx (PowerPoint)
  - pytesseract (OCR for images)
- **Language Detection**: langdetect
- **File Handling**: Werkzeug

##  Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | Run `pip install -r requirements.txt` |
| TTS generation fails | Check internet connection (online mode) or try offline mode |
| Image text extraction fails | Install Tesseract OCR |
| Port already in use | Change port in app.py or kill existing process |
| File upload fails | Check file size (<10MB) and format support |

##  Configuration

### Environment Variables
- `FLASK_DEBUG`: Enable/disable debug mode
- `MAX_CONTENT_LENGTH`: Maximum file upload size (default: 10MB)

### Supported File Types
- Documents: PDF, DOCX, DOC, PPTX, TXT
- Images: JPG, JPEG, PNG (requires Tesseract)

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request
