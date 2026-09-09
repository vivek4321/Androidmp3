from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from gtts import gTTS
import os
import uuid
from pathlib import Path
import librosa
import soundfile as sf
import numpy as np
from scipy import signal
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
CORS(app)

# Create audio directory
AUDIO_DIR = Path('public/audio')
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_file('public/index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_file(f'public/{path}')

@app.route('/api/convert', methods=['POST'])
def convert_text_to_mp3():
    """Convert text to MP3 using gTTS"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Please provide text to convert'}), 400
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.mp3"
        filepath = AUDIO_DIR / filename
        
        # Convert text to speech using Google TTS
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(str(filepath))
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': f'/audio/{filename}'
        }), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Failed to convert text to MP3'}), 500

@app.route('/api/modulate', methods=['POST'])
def modulate_audio():
    """Apply voice modulation effects to audio"""
    try:
        data = request.get_json()
        filename = data.get('filename', '')
        pitch_shift = float(data.get('pitch', 0))  # semitones
        speed = float(data.get('speed', 1.0))  # 0.5 to 2.0
        volume = float(data.get('volume', 1.0))  # 0.0 to 2.0
        effect = data.get('effect', 'none')  # none, echo, reverb, distortion
        
        if not filename:
            return jsonify({'error': 'No audio file provided'}), 400
        
        # Load audio
        audio_path = AUDIO_DIR / filename
        if not audio_path.exists():
            return jsonify({'error': 'Audio file not found'}), 404
        
        # Load audio file
        y, sr = librosa.load(str(audio_path), sr=None)
        
        # Apply pitch shift
        if pitch_shift != 0:
            y = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_shift)
        
        # Apply time stretch (speed)
        if speed != 1.0:
            y = librosa.effects.time_stretch(y, rate=speed)
        
        # Apply volume
        y = y * volume
        y = np.clip(y, -1, 1)  # Prevent clipping
        
        # Apply effects
        if effect == 'echo':
            y = apply_echo(y, sr)
        elif effect == 'reverb':
            y = apply_reverb(y, sr)
        elif effect == 'distortion':
            y = apply_distortion(y)
        
        # Save modulated audio
        output_filename = f"modulated_{uuid.uuid4()}.mp3"
        output_path = AUDIO_DIR / output_filename
        
        # Save as WAV first, then convert to MP3 if needed
        sf.write(str(output_path).replace('.mp3', '.wav'), y, sr)
        
        return jsonify({
            'success': True,
            'filename': output_filename,
            'url': f'/audio/{output_filename}'
        }), 200
        
    except Exception as e:
        print(f"Error in modulation: {str(e)}")
        return jsonify({'error': f'Failed to modulate audio: {str(e)}'}), 500

def apply_echo(y, sr, delay=0.5, decay=0.6):
    """Apply echo effect"""
    delay_samples = int(delay * sr)
    echo = np.zeros(len(y) + delay_samples)
    echo[:len(y)] = y
    echo[delay_samples:delay_samples + len(y)] += y * decay
    return echo[:len(y)]

def apply_reverb(y, sr, decay=0.3):
    """Apply simple reverb effect"""
    reverb = np.copy(y)
    for i in range(1, 5):
        delay_samples = int(0.05 * i * sr)
        if delay_samples < len(y):
            reverb[delay_samples:] += y[:-delay_samples] * (decay ** i)
    return np.clip(reverb, -1, 1)

def apply_distortion(y, amount=0.5):
    """Apply distortion effect"""
    distorted = y * (1 + amount * 2)
    return np.tanh(distorted)

def extract_fundamental_frequency(y, sr):
    """Extract fundamental frequency using spectral analysis"""
    try:
        # Use STFT for frequency analysis
        S = np.abs(librosa.stft(y))
        frequencies = librosa.fft_frequencies(sr=sr, n_fft=S.shape[0]*2-2)
        
        # Get the frequency with maximum magnitude
        f0_values = []
        for frame_idx in range(min(S.shape[1], 100)):  # Sample first 100 frames
            frame_mag = S[:, frame_idx]
            if len(frame_mag) > 10 and np.max(frame_mag) > 0:
                # Find peak frequency (skip DC and very low frequencies)
                peak_idx = np.argmax(frame_mag[10:]) + 10
                if peak_idx > 0 and peak_idx < len(frequencies):
                    f0 = frequencies[peak_idx]
                    if 50 < f0 < 500:  # Reasonable voice range
                        f0_values.append(f0)
        
        # Return median f0
        if f0_values:
            return float(np.median(f0_values))
        else:
            return 120.0
    except:
        return 120.0

def frequency_to_semitones(f1, f0=120):
    """Convert frequency difference to semitones"""
    if f1 <= 0:
        return 0
    return 12 * np.log2(f1 / f0)

def estimate_speaking_speed(y, sr):
    """Estimate speaking speed (1.0 = normal)"""
    try:
        # Detect onsets (syllables/phonemes)
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units='frames')
        
        # Calculate average time between onsets
        if len(onset_frames) > 2:
            # Convert frames to samples
            interval_samples = np.diff(onset_frames)
            avg_interval_samples = np.mean(interval_samples)
            avg_interval_time = avg_interval_samples / sr
            
            # 150ms is typical syllable duration
            if avg_interval_time > 0:
                speed = 0.15 / avg_interval_time
                return float(np.clip(speed, 0.5, 2.0))
        
        return 1.0
    except:
        return 1.0

@app.route('/api/analyze-voice', methods=['POST'])
def analyze_voice():
    """Analyze user's voice to get modulation settings"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Get file extension
        file_ext = os.path.splitext(file.filename)[1].lower() or '.wav'
        
        # Save uploaded file temporarily with proper extension
        temp_uploaded = tempfile.NamedTemporaryFile(suffix=file_ext, delete=False)
        file.save(temp_uploaded.name)
        temp_uploaded.close()
        
        try:
            # Try to load audio - librosa handles multiple formats
            # Use sr=None to preserve original sample rate
            try:
                y, sr = librosa.load(temp_uploaded.name, sr=None)
            except Exception as e:
                # If librosa fails, it might be a codec issue
                # Try with a common sr value
                print(f"Librosa load with sr=None failed: {e}")
                y, sr = librosa.load(temp_uploaded.name, sr=22050)
            
            # Ensure audio is long enough
            if len(y) < sr * 0.5:  # At least 0.5 seconds
                return jsonify({'error': 'Audio file too short (minimum 0.5 seconds)'}), 400
            
            # Extract fundamental frequency (pitch)
            f0 = extract_fundamental_frequency(y, sr)
            pitch_shift = frequency_to_semitones(f0, 120)  # 120 Hz is reference male voice
            
            # Estimate speaking speed
            speed = estimate_speaking_speed(y, sr)
            
            # Measure volume
            volume = np.sqrt(np.mean(y**2))
            volume_adjustment = 0.8 / volume if volume > 0 else 1.0
            volume_adjustment = float(np.clip(volume_adjustment, 0.5, 2.0))
            
            # Generate recommendations
            recommendations = {
                'pitch_shift': int(round(pitch_shift)),
                'speed': round(speed, 2),
                'volume': round(volume_adjustment, 2),
                'analysis': {
                    'fundamental_frequency': round(f0, 2),
                    'detected_volume': round(float(volume), 3),
                    'estimated_speed': round(speed, 2)
                }
            }
            
            return jsonify(recommendations), 200
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_uploaded.name):
                os.remove(temp_uploaded.name)
        
    except Exception as e:
        print(f"Error analyzing voice: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to analyze voice: {str(e)}'}), 500

@app.route('/audio/<filename>')
def get_audio(filename):
    """Serve audio files"""
    try:
        # Try both .mp3 and .wav
        filepath = (AUDIO_DIR / filename).resolve()
        if not filepath.exists():
            filepath = (AUDIO_DIR / filename.replace('.mp3', '.wav')).resolve()
        
        # Security check
        if not str(filepath).startswith(str(AUDIO_DIR.resolve())):
            return jsonify({'error': 'Access denied'}), 403
        
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        mime_type = 'audio/mpeg' if str(filepath).endswith('.mp3') else 'audio/wav'
        return send_file(str(filepath), mimetype=mime_type)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"🎵 Text to MP3 Converter running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
