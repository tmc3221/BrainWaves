#!/usr/bin/env python
"""Demo script for BrainWaves functionality (without requiring API key)."""

import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from brainwaves.embeddings import WordEmbeddings


def demo_word_embeddings():
    """Demonstrate word embedding functionality."""
    print("=" * 60)
    print("BrainWaves Demo - Word Embeddings")
    print("=" * 60)
    print()
    
    # Initialize embeddings
    print("Initializing word embeddings model...")
    embeddings = WordEmbeddings(model_name='glove-wiki-gigaword-50')
    
    # Test phrases
    test_phrases = [
        "jazz music",
        "meditation",
        "ambient soundscape",
        "nature sounds"
    ]
    
    print("\nGenerating semantic search queries:\n")
    
    for phrase in test_phrases:
        print(f"Input phrase: '{phrase}'")
        try:
            query = embeddings.build_semantic_query(phrase, num_terms=3)
            print(f"Generated query: '{query}'")
        except Exception as e:
            print(f"Error: {e}")
        print()
    
    print("=" * 60)
    print("Demo complete!")
    print()
    print("To use the full BrainWaves CLI:")
    print("1. Get a YouTube Data API v3 key")
    print("2. Create a .env file with: YOUTUBE_API_KEY=your_key")
    print("3. Run: python -m brainwaves.cli 'your phrase'")
    print("=" * 60)


if __name__ == '__main__':
    demo_word_embeddings()
