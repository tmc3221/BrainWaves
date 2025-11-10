"""Semantic word processing module using word embeddings."""

import random
from typing import List, Optional
from gensim.models import KeyedVectors
import gensim.downloader as api


class WordEmbeddings:
    """Handle word embeddings for semantic similarity."""
    
    def __init__(self, model_name: str = 'glove-wiki-gigaword-50'):
        """Initialize with a pre-trained word embedding model.
        
        Args:
            model_name: Name of the gensim model to use
        """
        self.model = None
        self.model_name = model_name
    
    def _ensure_model_loaded(self):
        """Lazy load the model when needed."""
        if self.model is None:
            print(f"Loading word embeddings model: {self.model_name}...")
            self.model = api.load(self.model_name)
            print("Model loaded successfully.")
    
    def get_similar_words(self, word: str, top_n: int = 10) -> List[str]:
        """Get semantically similar words.
        
        Args:
            word: The input word
            top_n: Number of similar words to retrieve
            
        Returns:
            List of similar words
        """
        self._ensure_model_loaded()
        
        # Normalize the word (lowercase, replace spaces with underscores)
        normalized_word = word.lower().replace(' ', '_')
        
        try:
            similar_words = self.model.most_similar(normalized_word, topn=top_n)
            return [word for word, _ in similar_words]
        except KeyError:
            # Word not in vocabulary, return empty list
            print(f"Warning: '{word}' not found in vocabulary.")
            return []
    
    def build_semantic_query(self, phrase: str, num_terms: int = 3) -> str:
        """Build a pseudo-random search query from a phrase.
        
        Args:
            phrase: Input word or phrase
            num_terms: Number of semantic terms to include
            
        Returns:
            A search query string combining original phrase and semantic terms
        """
        self._ensure_model_loaded()
        
        # Split phrase into words
        words = phrase.lower().split()
        
        # Collect similar words for each word in the phrase
        all_similar = []
        for word in words:
            similar = self.get_similar_words(word, top_n=15)
            all_similar.extend(similar)
        
        # Remove duplicates and select random terms
        unique_similar = list(set(all_similar))
        
        if unique_similar:
            # Randomly select some terms
            selected_terms = random.sample(
                unique_similar, 
                min(num_terms, len(unique_similar))
            )
        else:
            # Fallback if no similar words found
            selected_terms = []
        
        # Build the query
        query_parts = [phrase]
        query_parts.extend(selected_terms)
        
        return ' '.join(query_parts)
