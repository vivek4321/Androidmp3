# 🎵 Text to MP3 Converter with Voice Modulation & Voice Matcher

Convert any text into natural-sounding MP3 audio, apply voice modulation effects, and use Voice Matcher to automatically find settings that match your voice!

## ✨ Key Features

### 🎙️ Voice Matcher (NEW!)
- **Upload your voice** → App analyzes it
- **Auto-detects:**
  - Fundamental pitch frequency
  - Natural speaking speed
  - Volume level
- **One-click apply** → Settings auto-populate
- **Match any generated voice** to sound like you!

### Text-to-Speech
- 📝 Simple text input
- 🎙️ Natural-sounding voice (Google TTS)
- 🎵 High-quality MP3 output
- 🎧 Play or download audio

### Voice Modulation (Signal Processing)
- 🎚️ **Pitch Shift** - Change voice pitch (-12 to +12 semitones)
- ⏱️ **Speed Control** - Adjust playback speed (0.5x to 2.0x)
- 📢 **Volume Control** - Adjust volume (0 to 2.0)
- 🔊 **Audio Effects:**
  - **Echo** - Add echo effect
  - **Reverb** - Add reverb ambience
  - **Distortion** - Add distortion effect

## 📁 Project Structure

```
Androidmp3/
├── app.py              # Flask server with modulation API
├── public/
│   ├── index.html      # Frontend UI with controls
│   └── audio/          # Generated audio files
├── requirements.txt    # Python dependencies
├── run.sh             # Startup script
└── README.md          # This file
```

## 🎯 How It Works

1. **Enter text** → Click "Convert to MP3"
2. **Listen** to the generated audio
3. **Adjust settings:**
   - Pitch Shift slider
   - Speed slider
   - Volume slider
   - Select effect (Echo/Reverb/Distortion)
4. **Click "Apply Effects"**
5. **Download** the modulated MP3

## 🔧 Technologies Used

- **Backend:** Flask (Python)
- **Frontend:** HTML5 + CSS3 + JavaScript
- **TTS Engine:** Google gTTS
- **Audio Processing:** librosa, scipy, soundfile
- **Signal Processing:** NumPy-based algorithms

## 📦 Dependencies

- Flask - Web framework
- gTTS - Text-to-speech
- librosa - Audio analysis
- soundfile - Audio I/O
- scipy - Signal processing
- NumPy - Numerical computing

## 🎛️ Voice Modulation Details

### Pitch Shifting
- Range: -12 to +12 semitones
- Makes voice higher or lower
- Uses librosa's pitch shifting algorithm

### Speed Control
- Range: 0.5x to 2.0x
- 0.5x = half speed (slower)
- 2.0x = double speed (faster)
- Uses time-stretching algorithm

### Volume Control
- Range: 0 to 2.0
- 0 = silent
- 1.0 = original volume
- 2.0 = double volume

### Audio Effects
- **Echo**: Repeats sound with delay
- **Reverb**: Adds spacious ambience
- **Distortion**: Adds harmonic distortion

## 🛑 Stop Server

Press `CTRL+C` in the terminal

## 📝 Notes

- All processing done locally (no cloud upload)
- Audio files auto-cleanup after 1 hour
- Signal processing is fast (real-time capable)
- Works completely offline after first run

Enjoy! 🎵
