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
        """Build a vibe-focused search query from a phrase.
        
        Uses semantic similarity to find related terms and combines them
        with visual/audio-focused keywords for better media discovery.
        
        Args:
            phrase: Input word or phrase
            num_terms: Number of semantic terms to include
            
        Returns:
            A search query string optimized for visual/audio content
        """
        self._ensure_model_loaded()
        
        # Split phrase into words
        words = phrase.lower().split()
        
        # Collect similar words for each word in the phrase with higher similarity
        all_similar = []
        similarity_scores = {}
        
        for word in words:
            similar = self.get_similar_words(word, top_n=20)
            all_similar.extend(similar)
            # Track word presence for filtering
            for sim_word in similar:
                similarity_scores[sim_word] = similarity_scores.get(sim_word, 0) + 1
        
        # Remove duplicates, prioritize words that appear for multiple input words
        unique_similar = list(set(all_similar))
        
        # Filter out overly obscure or irrelevant terms
        # Keep terms that are more commonly associated with visual/audio content
        filtered_similar = [w for w in unique_similar if len(w) > 2 and not any(char.isdigit() for char in w)]
        
        # Sort by how many input words they're similar to (better relevance)
        filtered_similar.sort(key=lambda w: similarity_scores.get(w, 0), reverse=True)
        
        if filtered_similar:
            # Select top terms by relevance, not random
            selected_terms = filtered_similar[:min(num_terms, len(filtered_similar))]
        else:
            # Fallback if no similar words found
            selected_terms = []
        
        # Add vibe-enhancing terms for visual/audio content
        vibe_terms = ['music', 'visual', 'ambient', 'soundscape', 'audio']
        # Only add if not already in phrase or selected terms
        phrase_lower = phrase.lower()
        for vibe_term in vibe_terms:
            if vibe_term not in phrase_lower and vibe_term not in selected_terms:
                selected_terms.append(vibe_term)
                break  # Add just one vibe term
        
        # Build the query - phrase first, then most relevant semantic terms
        query_parts = [phrase]
        query_parts.extend(selected_terms[:num_terms])
        
        return ' '.join(query_parts)
