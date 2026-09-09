#!/bin/bash

# Text to MP3 Converter - Startup Script

echo "🎵 Text to MP3 Converter"
echo "========================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🚀 Starting server..."
echo "📍 Access the app at: http://localhost:3000"
echo ""
echo "Press CTRL+C to stop the server"
echo "================================"
echo ""

# Start the Flask server
python3 app.py
