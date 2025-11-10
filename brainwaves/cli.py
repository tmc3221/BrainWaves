"""Command-line interface for BrainWaves."""

import argparse
import sys
import webbrowser
from brainwaves.config import load_config
from brainwaves.embeddings import WordEmbeddings
from brainwaves.youtube import YouTubeSearch


def main():
    """Main entry point for the BrainWaves CLI."""
    parser = argparse.ArgumentParser(
        description='BrainWaves - Discover YouTube videos through semantic word exploration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  brainwaves "jazz music"
  brainwaves "meditation"
  brainwaves "ambient soundscape"
        """
    )
    
    parser.add_argument(
        'phrase',
        type=str,
        help='Word or phrase to explore'
    )
    
    parser.add_argument(
        '--num-terms',
        type=int,
        default=3,
        help='Number of semantic terms to include (default: 3)'
    )
    
    parser.add_argument(
        '--max-results',
        type=int,
        default=20,
        help='Maximum number of videos to fetch (default: 20)'
    )
    
    parser.add_argument(
        '--no-exclude-commentary',
        action='store_true',
        help='Do not exclude commentary/reaction videos'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='glove-wiki-gigaword-50',
        help='Word embedding model to use (default: glove-wiki-gigaword-50)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        print("Loading configuration...")
        config = load_config()
        
        # Initialize word embeddings
        print(f"\nProcessing phrase: '{args.phrase}'")
        embeddings = WordEmbeddings(model_name=args.model)
        
        # Build semantic query
        search_query = embeddings.build_semantic_query(
            args.phrase, 
            num_terms=args.num_terms
        )
        print(f"Generated search query: '{search_query}'")
        
        # Initialize YouTube search
        print("\nSearching YouTube...")
        youtube = YouTubeSearch(config['youtube_api_key'])
        
        # Get random video
        video = youtube.get_random_video(
            search_query,
            max_results=args.max_results
        )
        
        if video:
            print(f"\n✓ Found video:")
            print(f"  Title: {video['title']}")
            print(f"  URL: {video['url']}")
            print(f"\nOpening in browser...")
            webbrowser.open(video['url'])
            return 0
        else:
            print("\n✗ No videos found. Try a different phrase.")
            return 1
            
    except ValueError as e:
        print(f"\nConfiguration error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
