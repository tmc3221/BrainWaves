#!/bin/bash
# Installation script for BrainWaves Neon Visualizer

echo "==========================================="
echo "BrainWaves Neon Visualizer - Installation"
echo "==========================================="
echo

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed."
    echo "   Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js found: $(node --version)"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed."
    echo "   Please install npm (usually comes with Node.js)"
    exit 1
fi

echo "✓ npm found: $(npm --version)"
echo

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install Python dependencies"
    exit 1
fi
echo "✓ Python dependencies installed"
echo

# Install visualizer Node.js dependencies
echo "Installing visualizer Node.js dependencies..."
cd visualizer
npm install
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install visualizer dependencies"
    exit 1
fi
cd ..
echo "✓ Visualizer dependencies installed"
echo

echo "==========================================="
echo "✓ Installation complete!"
echo "==========================================="
echo
echo "Next steps:"
echo "1. Copy .env.example to .env"
echo "2. Add your YouTube API key to .env"
echo "3. Run: python launch_visualizer.py 'ambient music'"
echo
echo "For more information, see README.md"
