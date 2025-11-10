#!/usr/bin/env python
"""Quick demo showing BrainWaves architecture without heavy dependencies."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("=" * 70)
print("BrainWaves - Quick Architecture Demo")
print("=" * 70)
print()

print("📦 Checking package structure...")
print()

# Test imports
try:
    from brainwaves import __version__
    print(f"✓ Package version: {__version__}")
    
    from brainwaves.config import load_config
    print("✓ Config module imported")
    
    from brainwaves.embeddings import WordEmbeddings
    print("✓ Embeddings module imported")
    
    from brainwaves.youtube import YouTubeSearch
    print("✓ YouTube module imported")
    
    from brainwaves.cli import main
    print("✓ CLI module imported")
    
    print()
    print("=" * 70)
    print("🎉 All modules loaded successfully!")
    print("=" * 70)
    print()
    
    print("📋 Application Flow:")
    print("  1. Load configuration from .env (YouTube API key)")
    print("  2. Initialize word embeddings model (GloVe)")
    print("  3. Process user input phrase")
    print("  4. Find semantically similar words")
    print("  5. Build search query with exclusions")
    print("  6. Search YouTube Data API v3")
    print("  7. Select random video from results")
    print("  8. Open video in browser")
    print()
    
    print("=" * 70)
    print("🚀 To run the application:")
    print("  1. Create .env file with your YOUTUBE_API_KEY")
    print("  2. Run: python -m brainwaves.cli 'your phrase'")
    print("  3. Or install and use: brainwaves 'your phrase'")
    print("=" * 70)
    print()
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
