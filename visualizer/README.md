# BrainWaves Neon Visualizer

An Electron audio-reactive visualizer with canvas-based spectrum analyzer synchronized with YouTube videos.

## Features

- 🎬 **YouTube Video Streaming**: Uses yt-dlp (with @distube/ytdl-core fallback) for robust streaming
- 🎵 **Live Audio Analysis**: Captures audio from any microphone or system audio
- ✨ **Real-time Spectrum Analyzer**: Neon-style bars with bloom effects
- 🎮 **Interactive Controls**: Real-time effect parameter adjustment  
- ⚡ **Performance Optimized**: Capped DPR and reduced blur passes for smooth 60fps
- 📊 **Performance Monitoring**: FPS counter and status display

## Installation

### Prerequisites

**Required:**
- Node.js 18+ and npm

**Recommended for best video streaming:**
```bash
# Install yt-dlp for more reliable YouTube stream extraction
# On Linux/Mac:
pip install yt-dlp
# Or download from: https://github.com/yt-dlp/yt-dlp#installation
```

If yt-dlp is not available, the visualizer will automatically fall back to @distube/ytdl-core.

### Install Dependencies

```bash
cd visualizer
npm install
```

## Usage

### Launch with BrainWaves Semantic Search

Use the Python launcher to find and visualize videos based on semantic search:

```bash
# From the repository root
python launch_visualizer.py "ambient music"
python launch_visualizer.py "meditation sounds" --num-terms 5
```

### Launch with Direct URL

```bash
python launch_visualizer.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Launch Visualizer Directly

You can also launch the Electron app directly:

```bash
cd visualizer
npm start -- --video-url "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Controls

Use the on-screen sliders to adjust effects in real-time:

- **Bloom**: Brightness glow effect (0-3)
- **RGB Shift**: Chromatic aberration (0-0.02)
- **Glitch**: Digital glitch intensity (0-1)
- **Kaleidoscope**: Number of mirror segments (0-12)

## Audio Input

The visualizer will attempt to capture audio from:

1. **Primary**: Any available microphone (system default, Scarlett interface, laptop mic, etc.)
2. **Fallback**: Video audio stream

The visualizer will automatically detect and use your system's default audio input device. When audio is successfully connected, the device name will be displayed in the UI (e.g., "Audio: Built-in Microphone connected ✓").

For best results with external audio:
- Connect your audio source (music, instruments, etc.) to your audio interface
- Make sure the interface is set as the default recording device in your system settings
- Grant microphone permissions when prompted by the browser

## Architecture

### Components

- **main.js**: Electron main process, handles app lifecycle and window management
- **index.html**: UI structure and styling
- **visualizer.js**: Three.js renderer, audio analysis, and effect pipeline

### Audio Analysis

The visualizer uses Web Audio API to analyze audio in real-time:

- **Bass Band** (0-10% of spectrum): Drives RGB shift and kaleidoscope modulation
- **Mid Band** (10-50% of spectrum): Drives bloom intensity
- **High Band** (50-100% of spectrum): Drives glitch effect and neon glow

### Effects Pipeline

Effects are implemented using custom GLSL shaders:

1. **Kaleidoscope**: Mirror geometry based on polar coordinates
2. **Glitch**: Scanline-based position displacement
3. **RGB Shift**: Color channel separation along X-axis
4. **Bloom**: Brightness-threshold glow effect
5. **Neon Glow**: Cyan color addition based on high frequencies

## Development

Run in development mode with DevTools:

```bash
cd visualizer
npm run dev
```

## Troubleshooting

### "No video URL provided" error
Make sure to pass a video URL via the `--video-url` parameter or use the Python launcher.

### Video won't load or "Could not extract functions" error
The visualizer prefers `yt-dlp` for robust YouTube streaming and falls back to `@distube/ytdl-core`:
- **Best solution**: Install yt-dlp: `pip install yt-dlp` (see Installation section above)
- Ensure you have the latest dependencies: `cd visualizer && npm install`
- Some YouTube videos may have restrictions
- Try a different video or ensure you have a stable internet connection

### Performance issues / Laggy rendering
The visualizer is optimized for smooth 60fps with:
- DPR capped at 1.5 (reduces pixel count on high-DPI displays)
- Reduced blur passes (from 2 to 1)
- If still laggy, close other resource-intensive applications

### GetVSyncParametersIfAvailable errors in terminal
These are harmless Electron/GPU warnings (common on Wayland/Linux). They're suppressed in the latest version and don't affect functionality.

### No audio visualization
Check that your audio device is properly connected and that browser permissions for microphone access are granted.

### npm warnings about deprecated packages
The warning about `boolean@3.2.0` is from a transitive dependency and does not affect functionality.

## Requirements

- Node.js 18+ and npm
- Python 3.8+ (for BrainWaves integration)
- Internet connection (for video streaming)
- Audio input device (optional, for live audio reactivity)

## License

MIT License - Part of the BrainWaves project
