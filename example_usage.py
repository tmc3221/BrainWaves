#!/usr/bin/env python
"""
Example: Using BrainWaves Programmatically

This script demonstrates how to use BrainWaves modules in your own Python code.
"""

import os
from brainwaves.embeddings import WordEmbeddings
from brainwaves.youtube import YouTubeSearch

# Example 1: Using word embeddings only
print("=" * 70)
print("Example 1: Word Embeddings Only")
print("=" * 70)
print()

# Note: This will download the model on first run (~65MB)
# embeddings = WordEmbeddings(model_name='glove-wiki-gigaword-50')
# 
# phrase = "jazz music"
# print(f"Input phrase: '{phrase}'")
# 
# # Get similar words
# similar = embeddings.get_similar_words("jazz", top_n=5)
# print(f"Similar words to 'jazz': {similar}")
# 
# # Build semantic query
# query = embeddings.build_semantic_query(phrase, num_terms=3)
# print(f"Generated query: '{query}'")

print("(Commented out to avoid downloading model in demo)")
print()

# Example 2: YouTube search (requires API key)
print("=" * 70)
print("Example 2: YouTube Search")
print("=" * 70)
print()

api_key = os.getenv('YOUTUBE_API_KEY')
if api_key:
    youtube = YouTubeSearch(api_key)
    
    # Search for videos
    query = "ambient music chill relaxing"
    videos = youtube.search_videos(query, max_results=5)
    
    print(f"Found {len(videos)} videos for query: '{query}'")
    for i, video in enumerate(videos, 1):
        print(f"{i}. {video['title']}")
        print(f"   {video['url']}")
    
    # Get a random video
    random_video = youtube.get_random_video(query)
    if random_video:
        print(f"\nRandom selection: {random_video['title']}")
else:
    print("Set YOUTUBE_API_KEY environment variable to run this example")

print()
print("=" * 70)

# Example 3: Complete workflow
print("Example 3: Complete Workflow")
print("=" * 70)
print()

print("For the complete workflow, use the CLI:")
print()
print("  brainwaves 'your phrase'")
print()
print("Or import all modules:")
print()
print("  from brainwaves.config import load_config")
print("  from brainwaves.embeddings import WordEmbeddings")
print("  from brainwaves.youtube import YouTubeSearch")
print()
print("  config = load_config()")
print("  embeddings = WordEmbeddings()")
print("  youtube = YouTubeSearch(config['youtube_api_key'])")
print()
print("  query = embeddings.build_semantic_query('jazz')")
print("  video = youtube.get_random_video(query)")
print("  print(video['url'])")
print()
print("=" * 70)
