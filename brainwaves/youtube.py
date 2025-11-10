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
        exclude_commentary: bool = True
    ) -> List[Dict[str, str]]:
        """Search for videos on YouTube.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to fetch
            exclude_commentary: If True, exclude commentary/reaction videos
            
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
                '-discussion'
            ]
            search_query = f"{query} {' '.join(exclusions)}"
        
        try:
            # Call the search.list method
            search_response = self.youtube.search().list(
                q=search_query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                safeSearch='moderate'
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
        """Search and return a random video with fallback strategy.
        
        Args:
            query: Search query string (potentially enriched with semantic terms)
            max_results: Maximum number of results to fetch
            original_phrase: The original user phrase before semantic enrichment
            
        Returns:
            A random video dictionary or None if no videos found
        """
        # Try the enriched query first
        videos = self.search_videos(query, max_results=max_results)
        
        if videos:
            return random.choice(videos)
        
        # Fallback 1: Try without exclusions if we have the original phrase
        if original_phrase and original_phrase != query:
            print(f"No results with enriched query. Trying original phrase: '{original_phrase}'")
            videos = self.search_videos(original_phrase, max_results=max_results)
            if videos:
                return random.choice(videos)
        
        # Fallback 2: Try the query without commentary exclusions
        print("Trying without commentary exclusions...")
        videos = self.search_videos(query, max_results=max_results, exclude_commentary=False)
        
        if videos:
            return random.choice(videos)
        
        # Fallback 3: Try original phrase without exclusions
        if original_phrase and original_phrase != query:
            videos = self.search_videos(original_phrase, max_results=max_results, exclude_commentary=False)
            if videos:
                return random.choice(videos)
        
        return None
