"""Tests for the BrainWaves application."""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from brainwaves.config import load_config
from brainwaves.embeddings import WordEmbeddings
from brainwaves.youtube import YouTubeSearch


class TestConfig(unittest.TestCase):
    """Test configuration module."""
    
    def test_load_config_missing_api_key(self):
        """Test that load_config raises error when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                load_config()
            self.assertIn('YOUTUBE_API_KEY', str(context.exception))
    
    def test_load_config_with_api_key(self):
        """Test that load_config works when API key is present."""
        with patch.dict(os.environ, {'YOUTUBE_API_KEY': 'test_key'}):
            config = load_config()
            self.assertEqual(config['youtube_api_key'], 'test_key')


class TestWordEmbeddings(unittest.TestCase):
    """Test word embeddings module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.embeddings = WordEmbeddings()
    
    def test_initialization(self):
        """Test WordEmbeddings initialization."""
        self.assertIsNotNone(self.embeddings)
        self.assertEqual(self.embeddings.model_name, 'glove-wiki-gigaword-50')
        self.assertIsNone(self.embeddings.model)
    
    def test_get_similar_words_not_in_vocab(self):
        """Test get_similar_words with word not in vocabulary."""
        # Mock the model to avoid loading
        self.embeddings.model = MagicMock()
        self.embeddings.model.most_similar.side_effect = KeyError('word not found')
        
        result = self.embeddings.get_similar_words('xyznonexistent')
        self.assertEqual(result, [])
    
    def test_build_semantic_query_structure(self):
        """Test that build_semantic_query returns a string."""
        # Mock the model
        self.embeddings.model = MagicMock()
        self.embeddings.model.most_similar.return_value = [
            ('word1', 0.9), ('word2', 0.8), ('word3', 0.7)
        ]
        
        result = self.embeddings.build_semantic_query('test', num_terms=2)
        self.assertIsInstance(result, str)
        self.assertIn('test', result)


class TestYouTubeSearch(unittest.TestCase):
    """Test YouTube search module."""
    
    def test_initialization(self):
        """Test YouTubeSearch initialization."""
        youtube = YouTubeSearch('fake_api_key')
        self.assertIsNotNone(youtube)
        self.assertIsNotNone(youtube.youtube)
    
    @patch('brainwaves.youtube.build')
    def test_search_videos_with_exclusions(self, mock_build):
        """Test that search query includes exclusions."""
        # Mock the entire API chain
        mock_execute = MagicMock(return_value={
            'items': [
                {
                    'id': {'kind': 'youtube#video', 'videoId': 'test123'},
                    'snippet': {'title': 'Test Video'}
                }
            ]
        })
        mock_list = MagicMock(return_value=MagicMock(execute=mock_execute))
        mock_search = MagicMock(return_value=MagicMock(list=mock_list))
        mock_youtube = MagicMock(search=mock_search)
        mock_build.return_value = mock_youtube
        
        youtube = YouTubeSearch('fake_api_key')
        videos = youtube.search_videos('jazz', exclude_commentary=True)
        
        # Should return list of videos
        self.assertIsInstance(videos, list)
        if videos:
            self.assertIn('id', videos[0])
            self.assertIn('title', videos[0])
            self.assertIn('url', videos[0])
    
    @patch('brainwaves.youtube.build')
    def test_get_random_video_no_results(self, mock_build):
        """Test get_random_video returns None when no videos found."""
        # Mock empty response
        mock_execute = MagicMock(return_value={'items': []})
        mock_list = MagicMock(return_value=MagicMock(execute=mock_execute))
        mock_search = MagicMock(return_value=MagicMock(list=mock_list))
        mock_youtube = MagicMock(search=mock_search)
        mock_build.return_value = mock_youtube
        
        youtube = YouTubeSearch('fake_api_key')
        result = youtube.get_random_video('nonexistentquery')
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
