"""Configuration module for BrainWaves."""

import os
from dotenv import load_dotenv


def load_config():
    """Load configuration from .env file."""
    load_dotenv()
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        raise ValueError(
            "YOUTUBE_API_KEY not found in environment. "
            "Please create a .env file with your YouTube API key."
        )
    
    return {
        'youtube_api_key': api_key
    }
