/**
 * BrainWaves Neon Visualizer - Electron Main Process
 *
 * Handles window creation and app lifecycle
 */

const { app, BrowserWindow, ipcMain } = require('electron');
const { execFile } = require('child_process');
const path = require('path');
const url = require('url');

/**
 * Minimal browser global polyfills for Electron's main (Node) context.
 * We avoid requiring 'undici' here (that itself may assume File exists).
 * Define File (and Blob if needed) *before* any module that might import undici.
 */
(function ensureWebLikeGlobals() {
  // Provide Blob via Node's buffer module if missing
  if (typeof globalThis.Blob === 'undefined') {
    const { Blob } = require('buffer');
    globalThis.Blob = Blob;
  }

  // Provide a minimal File that satisfies libraries checking for its existence
  if (typeof globalThis.File === 'undefined') {
    const { Blob } = require('buffer');
    class File extends Blob {
      constructor(bits = [], name = '', opts = {}) {
        super(bits, opts);
        this.name = String(name);
        this.lastModified = opts.lastModified ?? Date.now();
      }
      get [Symbol.toStringTag]() {
        return 'File';
      }
    }
    globalThis.File = File;
  }

  // (Optional) Add fetch/FormData/etc. only if you later need them in main.
  // Avoid importing 'undici' here to prevent early initialization issues.
})();

// Suppress GPU-related warnings (common on Wayland/Linux)
// These must be set before app.on('ready')
app.commandLine.appendSwitch('disable-gpu-vsync');
app.commandLine.appendSwitch('disable-features', 'VizDisplayCompositor');

let mainWindow;

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 720,
    backgroundColor: '#000000',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    title: 'BrainWaves Neon Visualizer',
    autoHideMenuBar: true
  });

  // Parse command line arguments or use default
  const args = process.argv.slice(1);
  let videoUrl = null;

  // Look for --video-url parameter
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--video-url' && i + 1 < args.length) {
      videoUrl = args[i + 1];
      break;
    }
  }

  // Build the URL with video parameter if provided
  const indexPath = path.join(__dirname, 'index.html');
  const indexUrl = url.format({
    pathname: indexPath,
    protocol: 'file:',
    slashes: true,
    query: videoUrl ? { video: videoUrl } : {}
  });

  mainWindow.loadURL(indexUrl);

  // Open DevTools in development mode
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// Handle video URL messages from renderer
ipcMain.on('get-video-url', (event) => {
  const args = process.argv.slice(1);
  let videoUrl = null;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--video-url' && i + 1 < args.length) {
      videoUrl = args[i + 1];
      break;
    }
  }

  event.reply('video-url', videoUrl);
});

// Handle video stream URL extraction from YouTube
ipcMain.handle('get-video-stream-url', async (event, youtubeUrl) => {
  const tryYtDlp = async () => {
    // Ask yt-dlp for ONE direct URL, preferring a muxed MP4.
    // If no mp4, take best available single URL.
    const args = ['-g', '-f', 'best[ext=mp4]/best', youtubeUrl];

    return new Promise((resolve, reject) => {
      execFile('yt-dlp', args, { maxBuffer: 10 * 1024 * 1024 }, (err, stdout, stderr) => {
        if (err) return reject(new Error(`yt-dlp failed: ${stderr || err.message}`));
        const lines = stdout.trim().split('\n').filter(Boolean);
        if (lines.length === 0) return reject(new Error('yt-dlp returned no URLs'));

        // We requested a single muxed format; take the first line.
        const streamUrl = lines[0];

        resolve({
          streamUrl,
          title: null,
          duration: null
        });
      });
    });
  };

  const tryYtdlCore = async () => {
    // Lazy-load only after global stubs/polyfills exist
    const ytdl = require('@distube/ytdl-core');

    // You can pass the whole URL; no need to extract ID
    const info = await ytdl.getInfo(youtubeUrl);

    // Prefer best muxed (video+audio)
    const format = ytdl.chooseFormat(info.formats, {
      quality: 'highest',
      filter: 'videoandaudio'
    });

    if (!format || !format.url) {
      throw new Error('No suitable format from ytdl-core');
    }

    return {
      streamUrl: format.url,
      title: info.videoDetails?.title || 'YouTube',
      duration: info.videoDetails?.lengthSeconds || null
    };
  };

  try {
    console.log('Extracting video stream URL from:', youtubeUrl);

    // Prefer yt-dlp (more resilient to cipher changes)
    try {
      const r = await tryYtDlp();
      return { success: true, ...r };
    } catch (e) {
      console.warn('yt-dlp unavailable or failed; falling back to ytdl-core:', e.message);
      const r = await tryYtdlCore();
      return { success: true, ...r };
    }
  } catch (error) {
    console.error('Error extracting video stream URL:', error);
    return { success: false, error: error.message };
  }
});

/**
 * Extract video ID from YouTube URL
 */
function extractVideoId(u) {
  const regex = /(?:youtube\.com\/(?:[^/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?/\\s]{11})/;
  const match = u && typeof u === 'string' ? u.match(regex) : null;
  return match ? match[1] : null;
}

