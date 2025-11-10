# BrainWaves Development Guide

## Project Structure

```
BrainWaves/
├── brainwaves/              # Main application package
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # Command-line interface
│   ├── config.py            # Configuration management (.env)
│   ├── embeddings.py        # Word embedding functionality
│   └── youtube.py           # YouTube API integration
├── tests/                   # Unit tests
│   ├── __init__.py
│   └── test_brainwaves.py   # Test suite
├── .env.example             # Example environment configuration
├── .gitignore               # Git ignore patterns
├── demo.py                  # Full demo with word embeddings
├── quick_demo.py            # Quick architecture verification
├── README.md                # User documentation
├── requirements.txt         # Python dependencies
├── setup.py                 # Package installation configuration
└── DEVELOPMENT.md           # This file
```

## Architecture Overview

BrainWaves follows a modular architecture designed for maintainability and extensibility:

### Core Modules

1. **config.py** - Configuration Management
   - Loads environment variables from .env file
   - Validates required configuration
   - Returns configuration dictionary

2. **embeddings.py** - Semantic Word Processing
   - Lazy-loads GloVe word embedding models
   - Finds semantically similar words
   - Builds pseudo-random search queries
   - Handles out-of-vocabulary words gracefully

3. **youtube.py** - YouTube API Integration
   - Wraps YouTube Data API v3 client
   - Implements video search with filtering
   - Excludes commentary/reaction content
   - Returns random video selection

4. **cli.py** - Command-Line Interface
   - Parses command-line arguments
   - Orchestrates the workflow
   - Provides user-friendly output
   - Opens videos in default browser

## Development Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- YouTube Data API v3 key

### Installation
```bash
# Clone the repository
git clone https://github.com/tmc3221/BrainWaves.git
cd BrainWaves

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your YouTube API key
YOUTUBE_API_KEY=your_actual_api_key_here
```

## Testing

### Running Tests
```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test class
python -m unittest tests.test_brainwaves.TestConfig -v

# Run specific test method
python -m unittest tests.test_brainwaves.TestConfig.test_load_config_with_api_key -v
```

### Test Coverage
The test suite includes:
- Configuration loading and validation
- Word embedding initialization and operations
- YouTube API client initialization
- Video search and filtering
- Error handling for missing API keys
- Edge cases (empty results, missing words)

## Usage Examples

### Basic Usage
```bash
# Simple phrase
brainwaves "jazz"

# Multi-word phrase
brainwaves "ambient soundscape"
```

### Advanced Options
```bash
# Increase semantic terms
brainwaves "meditation" --num-terms 5

# Increase result pool
brainwaves "nature sounds" --max-results 30

# Include commentary videos
brainwaves "jazz" --no-exclude-commentary

# Use different embedding model
brainwaves "classical" --model glove-wiki-gigaword-100
```

## Code Style

The project follows PEP 8 style guidelines:
- 4 spaces for indentation
- Max line length: 88-100 characters
- Docstrings for all public functions/classes
- Type hints where appropriate

## Extending BrainWaves

### Adding New Word Embedding Models

Edit `brainwaves/embeddings.py`:
```python
# Add new model option in WordEmbeddings.__init__
def __init__(self, model_name: str = 'your-new-model'):
    self.model_name = model_name
```

### Adding New Video Filters

Edit `brainwaves/youtube.py`:
```python
# Modify exclusion list in search_videos method
exclusions = [
    '-reaction',
    '-review',
    '-your-new-filter'
]
```

### Creating a Web Interface

The modular design makes web integration straightforward:

```python
from flask import Flask, jsonify, request
from brainwaves.embeddings import WordEmbeddings
from brainwaves.youtube import YouTubeSearch
from brainwaves.config import load_config

app = Flask(__name__)

# Initialize once at startup
config = load_config()
embeddings = WordEmbeddings()
youtube = YouTubeSearch(config['youtube_api_key'])

@app.route('/api/discover', methods=['POST'])
def discover():
    phrase = request.json.get('phrase')
    query = embeddings.build_semantic_query(phrase)
    video = youtube.get_random_video(query)
    return jsonify(video)

if __name__ == '__main__':
    app.run(debug=True)
```

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure you're in the project directory
   - Verify virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **"YOUTUBE_API_KEY not found"**
   - Create .env file in project root
   - Add your API key: `YOUTUBE_API_KEY=your_key`
   - Ensure .env is not in .gitignore (it is by default)

3. **"Word not found in vocabulary"**
   - Some words aren't in the GloVe vocabulary
   - The app continues but without semantic expansion
   - Try more common words or phrases

4. **Slow first run**
   - First run downloads ~65MB word embedding model
   - Model is cached for subsequent runs
   - Use smaller model: `--model glove-wiki-gigaword-50`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Ensure all tests pass
6. Submit a pull request

## Security Considerations

- API keys are loaded from .env (not committed)
- No user input is executed as code
- YouTube API calls use official client library
- Dependencies are from trusted sources

## Performance Notes

- Word embedding model loading: ~2-5 seconds (first run only)
- YouTube API call: ~1-2 seconds
- Overall execution: ~3-7 seconds (after initial setup)

## Future Enhancements

Potential areas for expansion:
- [ ] Add more embedding model options
- [ ] Implement result caching
- [ ] Add web interface (Flask/FastAPI)
- [ ] Support multiple video platforms
- [ ] Add user preferences/history
- [ ] Implement playlist generation
- [ ] Add music genre detection
- [ ] Support for different languages

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/tmc3221/BrainWaves/issues
- Pull Requests: https://github.com/tmc3221/BrainWaves/pulls
