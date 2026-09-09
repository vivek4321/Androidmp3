# 🎵 Text to MP3 Converter

Convert any text into natural-sounding MP3 audio using Google Text-to-Speech.

## 🚀 Quick Start

### First Time Setup (One-time)
```bash
pip install -r requirements.txt
```

### Run the Server
```bash
python3 app.py
```

Or use the startup script:
```bash
bash run.sh
```

**Access at:** `http://localhost:3000`

## ✨ Features

- 📝 Simple text input
- 🎙️ Natural-sounding voice (Google TTS)
- 🎵 High-quality MP3 output
- 🎧 Play or download audio
- ⚡ Instant conversion

## 📁 Project Structure

```
Androidmp3/
├── app.py              # Flask server (main backend)
├── public/
│   ├── index.html      # Frontend UI
│   └── audio/          # Generated MP3 files
├── requirements.txt    # Python dependencies
├── run.sh             # Startup script
└── README.md          # This file
```

## 🔧 How It Works

1. **Enter text** in the web interface
2. **Click "Convert to MP3"**
3. **Listen** in the browser or download

## 📦 Requirements

- Python 3.8+
- Flask
- gTTS (Google Text-to-Speech)

## 🎯 What's Inside

- **Backend:** Flask (Python)
- **Frontend:** HTML5 + CSS3 + JavaScript
- **TTS Engine:** Google's gTTS (free, no API key needed)

## 🛑 Stop Server

Press `CTRL+C` in the terminal

## 📝 Notes

- No configuration needed
- Works completely offline after first run
- Free to use
- Audio files auto-cleanup after 1 hour

Enjoy! 🎵
