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
        """Build a trippy, transformative search query from a phrase.
        
        Creates unexpected but semantically related queries by mixing and
        replacing words rather than just appending. Optimized for discovering
        trippy visual/audio content for visualizers.
        
        Args:
            phrase: Input word or phrase
            num_terms: Number of semantic terms to include in transformation
            
        Returns:
            A transformed search query that's related but unexpected
        """
        self._ensure_model_loaded()
        
        # Split phrase into words
        words = phrase.lower().split()
        
        # Collect similar words for each word in the phrase
        word_alternatives = {}
        for word in words:
            similar = self.get_similar_words(word, top_n=30)
            # Filter out obscure terms but keep interesting ones
            filtered = [w for w in similar if len(w) > 2 and not any(char.isdigit() for char in w)]
            word_alternatives[word] = filtered[:15] if filtered else []
        
        # Trippy transformation strategies - randomly choose one
        strategy = random.choice(['mix', 'replace', 'surround', 'inject'])
        
        if strategy == 'mix' and word_alternatives:
            # Mix original words with semantic alternatives
            query_words = []
            for word in words:
                # 50% chance to replace each word with a semantic alternative
                if random.random() > 0.5 and word in word_alternatives and word_alternatives[word]:
                    query_words.append(random.choice(word_alternatives[word]))
                else:
                    query_words.append(word)
            # Add some extra semantic terms
            all_alts = [alt for alts in word_alternatives.values() for alt in alts]
            if all_alts:
                extra = random.sample(all_alts, min(num_terms, len(all_alts)))
                query_words.extend(extra)
        
        elif strategy == 'replace' and word_alternatives:
            # Replace words with semantic neighbors for a trippy effect
            query_words = []
            for word in words:
                if word in word_alternatives and word_alternatives[word]:
                    # Pick from top alternatives with some randomness
                    alt_choices = word_alternatives[word][:5]
                    query_words.append(random.choice(alt_choices))
                else:
                    query_words.append(word)
            # Add vibe-enhancing visual terms
            vibe_terms = ['psychedelic', 'hypnotic', 'ethereal', 'cosmic', 'surreal', 'dreamlike']
            query_words.append(random.choice(vibe_terms))
        
        elif strategy == 'surround':
            # Surround original with semantic context for trippy discovery
            all_alts = [alt for alts in word_alternatives.values() for alt in alts]
            if all_alts and len(all_alts) >= num_terms * 2:
                # Pick random semantic terms from middle range (not too similar, not too distant)
                mid_range_start = min(5, len(all_alts) // 3)
                mid_range_end = min(20, (len(all_alts) * 2) // 3)
                mid_range = all_alts[mid_range_start:mid_range_end]
                if mid_range:
                    before = random.sample(mid_range, min(num_terms, len(mid_range)))
                    after = random.sample(mid_range, min(num_terms, len(mid_range)))
                    query_words = before + words + after
                else:
                    query_words = words + all_alts[:num_terms]
            else:
                query_words = words
        
        else:  # 'inject' strategy
            # Inject semantic terms between original words
            query_words = []
            all_alts = [alt for alts in word_alternatives.values() for alt in alts]
            for i, word in enumerate(words):
                query_words.append(word)
                # Inject semantic term after each word (except last)
                if i < len(words) - 1 and all_alts:
                    query_words.append(random.choice(all_alts[:15]))
            # Add visual/audio contextual terms
            vibe_terms = ['visual', 'sonic', 'ambient', 'atmospheric', 'immersive']
            if vibe_terms:
                query_words.append(random.choice(vibe_terms))
        
        # Ensure we have something
        if not query_words:
            query_words = words
        
        return ' '.join(query_words[:8])  # Limit to 8 terms max for YouTube API
