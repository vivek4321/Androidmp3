from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from gtts import gTTS
import os
import uuid
from pathlib import Path

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

@app.route('/audio/<filename>')
def get_audio(filename):
    """Serve audio files"""
    try:
        filepath = (AUDIO_DIR / filename).resolve()
        
        # Security check
        if not str(filepath).startswith(str(AUDIO_DIR.resolve())):
            return jsonify({'error': 'Access denied'}), 403
        
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(str(filepath), mimetype='audio/mpeg')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"🎵 Text to MP3 Converter running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
