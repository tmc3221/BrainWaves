#!/usr/bin/env python3
"""
Demo script for BrainWaves Neon Visualizer

This demonstrates launching the visualizer with a test video.
"""

import subprocess
import sys
import os

def main():
    """Run a demo of the visualizer with a sample ambient music video."""
    
    # Sample YouTube URL - public domain ambient music
    # Using a well-known ambient music video that should work
    demo_url = "https://www.youtube.com/watch?v=jfKfPfyJRdk"  # lofi hip hop radio
    
    print("=" * 60)
    print("BrainWaves Neon Visualizer - Demo")
    print("=" * 60)
    print()
    print("This will launch the visualizer with a sample video.")
    print("The visualizer features:")
    print("  - Real-time audio analysis")
    print("  - Audio-reactive visual effects")
    print("  - Interactive effect controls")
    print()
    print(f"Demo video: {demo_url}")
    print()
    
    response = input("Launch visualizer? (y/n): ")
    
    if response.lower() != 'y':
        print("Demo cancelled.")
        return
    
    print("\nLaunching visualizer...")
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    launcher_path = os.path.join(script_dir, 'launch_visualizer.py')
    
    try:
        subprocess.run([
            sys.executable,
            launcher_path,
            '--url',
            demo_url
        ])
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
