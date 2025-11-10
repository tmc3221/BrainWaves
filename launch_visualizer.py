#!/usr/bin/env python3
"""
BrainWaves Visualizer Launcher

Launches the Electron visualizer with a BrainWaves-selected video URL
"""

import argparse
import subprocess
import sys
import os
from brainwaves.config import load_config
from brainwaves.embeddings import WordEmbeddings
from brainwaves.youtube import YouTubeSearch


def launch_visualizer(video_url):
    """Launch the Electron visualizer with the given video URL.
    
    Args:
        video_url: YouTube video URL to visualize
    """
    visualizer_path = os.path.join(os.path.dirname(__file__), 'visualizer')
    
    # Check if visualizer exists
    if not os.path.exists(visualizer_path):
        print("Error: Visualizer not found. Please run 'npm install' in the visualizer directory.")
        return False
    
    # Check if node_modules exists
    node_modules = os.path.join(visualizer_path, 'node_modules')
    if not os.path.exists(node_modules):
        print("Installing visualizer dependencies...")
        try:
            subprocess.run(['npm', 'install'], cwd=visualizer_path, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            return False
    
    print(f"\n🌊 Launching BrainWaves Neon Visualizer...")
    print(f"Video: {video_url}\n")
    
    try:
        # Launch Electron with video URL
        subprocess.run(
            ['npm', 'start', '--', '--video-url', video_url],
            cwd=visualizer_path
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error launching visualizer: {e}")
        return False
    except FileNotFoundError:
        print("Error: npm not found. Please install Node.js and npm.")
        return False


def main():
    """Main entry point for the visualizer launcher."""
    parser = argparse.ArgumentParser(
        description='BrainWaves Neon Visualizer - Launch audio-reactive video visualizer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch with semantic search
  python launch_visualizer.py "ambient music"
  
  # Launch with direct URL
  python launch_visualizer.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
  
  # Adjust semantic search parameters
  python launch_visualizer.py "meditation sounds" --num-terms 5
        """
    )
    
    parser.add_argument(
        'phrase',
        nargs='?',
        type=str,
        help='Word or phrase to explore (not needed if --url is provided)'
    )
    
    parser.add_argument(
        '--url',
        type=str,
        help='Direct YouTube URL to visualize (skips search)'
    )
    
    parser.add_argument(
        '--num-terms',
        type=int,
        default=3,
        help='Number of semantic terms to include in search (default: 3)'
    )
    
    parser.add_argument(
        '--max-results',
        type=int,
        default=20,
        help='Maximum number of videos to fetch for search (default: 20)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='glove-wiki-gigaword-50',
        help='Word embedding model to use (default: glove-wiki-gigaword-50)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.url and not args.phrase:
        parser.error("Either provide a phrase or use --url to specify a direct YouTube URL")
    
    try:
        video_url = None
        
        if args.url:
            # Use direct URL
            video_url = args.url
            print(f"Using provided URL: {video_url}")
            
        else:
            # Use BrainWaves semantic search
            print("Loading configuration...")
            config = load_config()
            
            print(f"Processing phrase: '{args.phrase}'")
            embeddings = WordEmbeddings(model_name=args.model)
            
            # Build semantic query
            search_query = embeddings.build_semantic_query(
                args.phrase, 
                num_terms=args.num_terms
            )
            print(f"Generated search query: '{search_query}'")
            
            # Initialize YouTube search
            print("Searching YouTube...")
            youtube = YouTubeSearch(config['youtube_api_key'])
            
            # Get random video
            video = youtube.get_random_video(
                search_query,
                max_results=args.max_results,
                original_phrase=args.phrase
            )
            
            if video:
                print(f"\n✓ Found video:")
                print(f"  Title: {video['title']}")
                print(f"  URL: {video['url']}")
                video_url = video['url']
            else:
                print("\n✗ No videos found. Try a different phrase.")
                return 1
        
        # Launch visualizer
        if video_url:
            success = launch_visualizer(video_url)
            return 0 if success else 1
        
    except ValueError as e:
        print(f"\nConfiguration error: {e}")
        print("Make sure you have a .env file with your YOUTUBE_API_KEY")
        return 1
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
