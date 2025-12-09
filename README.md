# BrainWaves

Word -> Vibes

A Python CLI application that takes any word or phrase, finds semantically adjacent terms using word embeddings, and discovers related YouTube videos through intelligent search.

## Features

- 🧠 **Semantic Word Exploration**: Uses word embeddings (GloVe) to find semantically related terms
- 🎬 **Smart YouTube Search**: Automatically excludes commentary, reaction, and review videos
- 🎲 **Random Discovery**: Returns a random video from the search results
- 🌐 **Browser Integration**: Opens the selected video directly in your browser
- 🌊 **Neon Visualizer**: Audio-reactive video visualizer with real-time effects (Xbox 360-style)
- 🔧 **Modular Design**: Clean architecture ready for Flask/web integration
- 🔐 **Secure Configuration**: Uses .env files for API key management

## Installation

### Quick Install (Recommended)

Use the installation script to set up both Python and visualizer dependencies:

```bash
git clone https://github.com/tmc3221/BrainWaves.git
cd BrainWaves
chmod +x install.sh
./install.sh
```

Then set up your YouTube API key:
- Get a YouTube Data API v3 key from [Google Cloud Console](https://console.cloud.google.com/)
- Copy `.env.example` to `.env`: `cp .env.example .env`
- Edit `.env` and add your API key: `YOUTUBE_API_KEY=your_actual_api_key_here`

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/tmc3221/BrainWaves.git
cd BrainWaves
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install visualizer dependencies (for Neon Visualizer):
```bash
cd visualizer
npm install
cd ..
```

4. Set up your YouTube API key:
   - Get a YouTube Data API v3 key from [Google Cloud Console](https://console.cloud.google.com/)
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your API key:
     ```
     YOUTUBE_API_KEY=your_actual_api_key_here
     ```

5. Install the package (optional, for system-wide `brainwaves` command):
```bash
pip install -e .
```

## Usage

### Basic Usage

Run with a word or phrase:
```bash
python -m brainwaves.cli "jazz music"
```

Or if installed:
```bash
brainwaves "meditation"
```

### Advanced Options

```bash
# Specify number of semantic terms to include (default: 3)
brainwaves "ambient soundscape" --num-terms 5

# Change maximum results to fetch (default: 20)
brainwaves "nature sounds" --max-results 30

# Include commentary/reaction videos (excluded by default)
brainwaves "jazz" --no-exclude-commentary

# Use a different word embedding model
brainwaves "classical" --model glove-wiki-gigaword-100
```

### Examples

```bash
# Discover ambient music
brainwaves "ambient"

# Explore meditation content
brainwaves "meditation sounds"

# Find jazz-related videos
brainwaves "bebop jazz"
```

### Neon Visualizer

Launch the audio-reactive visualizer with semantic search:

```bash
# Launch visualizer with BrainWaves search
python launch_visualizer.py "ambient music"

# Launch with more semantic terms
python launch_visualizer.py "meditation sounds" --num-terms 5

# Launch with direct YouTube URL
python launch_visualizer.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

The visualizer features:
- Real-time audio analysis (bass/mid/high frequencies)
- Audio-reactive effects: Bloom, RGB Shift, Glitch, Kaleidoscope
- Interactive controls for effect parameters
- Supports Scarlett audio interface or system audio

For more details, see [visualizer/README.md](visualizer/README.md).

## How It Works

1. **Semantic Analysis**: Takes your input phrase and uses pre-trained GloVe word embeddings to find semantically similar words
2. **Query Building**: Constructs a pseudo-random search query combining your phrase with related terms
3. **Smart Filtering**: Applies negative keywords to exclude commentary, reactions, and reviews
4. **Video Discovery**: Searches YouTube Data API v3 with the enhanced query
5. **Random Selection**: Picks a random video from the results
6. **Browser Launch**: Opens the selected video in your default browser

## Project Structure

```
BrainWaves/
├── brainwaves/
│   ├── __init__.py       # Package initialization
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Configuration management
│   ├── embeddings.py     # Word embedding functionality
│   └── youtube.py        # YouTube API integration
├── .env.example          # Example environment variables
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
├── setup.py            # Package setup configuration
└── README.md           # This file
```

## Modular Architecture

BrainWaves is designed with modularity in mind, making it easy to integrate into other applications:

- **`config.py`**: Handles environment configuration
- **`embeddings.py`**: Manages word embeddings and semantic similarity
- **`youtube.py`**: YouTube API client for video search
- **`cli.py`**: Command-line interface (can be extended for web/Flask)

### Future Web/Flask Integration

The modular design allows easy integration with Flask:

```python
from flask import Flask, jsonify
from brainwaves.embeddings import WordEmbeddings
from brainwaves.youtube import YouTubeSearch
from brainwaves.config import load_config

app = Flask(__name__)
config = load_config()
embeddings = WordEmbeddings()
youtube = YouTubeSearch(config['youtube_api_key'])

@app.route('/discover/<phrase>')
def discover(phrase):
    query = embeddings.build_semantic_query(phrase)
    video = youtube.get_random_video(query)
    return jsonify(video)
```

## Dependencies

- `google-api-python-client`: YouTube Data API v3 client
- `python-dotenv`: Environment variable management
- `gensim`: Word embedding models
- `numpy`: Numerical computations

## Requirements

### Core Requirements
- Python 3.8 or higher
- YouTube Data API v3 key
- Internet connection (for downloading word embeddings and API calls)

### Visualizer Requirements
- Node.js 18+ and npm (for Neon Visualizer)
- Audio input device (optional, for live audio reactivity)
- Modern web browser with WebGL support

## License

MIT License

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Troubleshooting

### "Word not found in vocabulary"
Some specialized or compound words might not be in the GloVe vocabulary. The app will still work but won't add semantic terms for those words.

### "Configuration error: YOUTUBE_API_KEY not found"
Make sure you've created a `.env` file with your YouTube API key. See Installation step 3.

### First run is slow
The first time you run BrainWaves, it needs to download the word embedding model (~65 MB). Subsequent runs will be much faster.
