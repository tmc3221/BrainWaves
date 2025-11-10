"""YouTube API integration module."""

import random
from typing import List, Dict, Optional
from googleapiclient.discovery import build


class YouTubeSearch:
    """Handle YouTube video search using the Data API v3."""
    
    def __init__(self, api_key: str):
        """Initialize YouTube API client.
        
        Args:
            api_key: YouTube Data API v3 key
        """
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def search_videos(
        self, 
        query: str, 
        max_results: int = 20,
        exclude_commentary: bool = True,
        prefer_visual_audio: bool = True
    ) -> List[Dict[str, str]]:
        """Search for videos on YouTube.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to fetch
            exclude_commentary: If True, exclude commentary/reaction videos
            prefer_visual_audio: If True, optimize for visual/audio content
            
        Returns:
            List of video dictionaries with 'id', 'title', and 'url'
        """
        # Build search query with exclusions
        search_query = query
        
        if exclude_commentary:
            # Add negative keywords to exclude commentary/reaction videos
            exclusions = [
                '-reaction',
                '-review',
                '-commentary',
                '-podcast',
                '-interview',
                '-talk',
                '-discussion',
                '-tutorial',
                '-howto',
                '-explained'
            ]
            search_query = f"{query} {' '.join(exclusions)}"
        
        try:
            # Call the search.list method
            search_response = self.youtube.search().list(
                q=search_query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                safeSearch='moderate',
                videoDuration='medium'  # Prefer medium+ length for visualizers
            ).execute()
            
            videos = []
            for item in search_response.get('items', []):
                if item['id']['kind'] == 'youtube#video':
                    video_id = item['id']['videoId']
                    videos.append({
                        'id': video_id,
                        'title': item['snippet']['title'],
                        'url': f"https://www.youtube.com/watch?v={video_id}"
                    })
            
            return videos
            
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return []
    
    def get_random_video(
        self, 
        query: str, 
        max_results: int = 20,
        original_phrase: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """Search and return a random video with intelligent fallback strategy.
        
        Tries to maintain semantic enrichment as long as possible before
        falling back to simpler queries. Optimized for visual/audio content.
        
        Args:
            query: Search query string (potentially enriched with semantic terms)
            max_results: Maximum number of results to fetch
            original_phrase: The original user phrase before semantic enrichment
            
        Returns:
            A random video dictionary or None if no videos found
        """
        # Try the enriched query first with all exclusions
        videos = self.search_videos(query, max_results=max_results, exclude_commentary=True)
        
        if videos:
            return random.choice(videos)
        
        # Fallback 1: Reduce exclusions but keep the enriched query
        # This maintains the semantic vibe while being less restrictive
        print(f"Adjusting query restrictions for better results...")
        videos = self.search_videos(query, max_results=max_results, exclude_commentary=False)
        
        if videos:
            return random.choice(videos)
        
        # Fallback 2: Try with just the original phrase but keep some visual context
        if original_phrase and original_phrase != query:
            # Add generic visual/audio terms to original phrase
            enhanced_original = f"{original_phrase} music visual audio"
            print(f"Trying enhanced original query: '{enhanced_original}'")
            videos = self.search_videos(enhanced_original, max_results=max_results, exclude_commentary=False)
            if videos:
                return random.choice(videos)
        
        # Fallback 3: Just the original phrase with minimal restrictions
        if original_phrase and original_phrase != query:
            print(f"Trying original phrase: '{original_phrase}'")
            videos = self.search_videos(original_phrase, max_results=max_results, exclude_commentary=False)
            if videos:
                return random.choice(videos)
        
        return None
