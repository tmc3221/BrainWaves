/**
 * BrainWaves Neon Visualizer - Electron Main Process
 * 
 * Handles window creation and app lifecycle
 */

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const url = require('url');
const ytdl = require('@distube/ytdl-core');

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
  try {
    console.log('Extracting video stream URL from:', youtubeUrl);
    
    // Extract video ID
    const videoId = extractVideoId(youtubeUrl);
    if (!videoId) {
      throw new Error('Invalid YouTube URL');
    }
    
    // Get video info
    const info = await ytdl.getInfo(videoId);
    
    // Choose best video format with audio
    const format = ytdl.chooseFormat(info.formats, { 
      quality: 'highest',
      filter: 'videoandaudio'
    });
    
    if (!format) {
      throw new Error('No suitable video format found');
    }
    
    console.log('Found video format:', format.qualityLabel, format.container);
    
    return {
      success: true,
      streamUrl: format.url,
      title: info.videoDetails.title,
      duration: info.videoDetails.lengthSeconds
    };
    
  } catch (error) {
    console.error('Error extracting video stream URL:', error);
    return {
      success: false,
      error: error.message
    };
  }
});

/**
 * Extract video ID from YouTube URL
 */
function extractVideoId(url) {
  const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
  const match = url.match(regex);
  return match ? match[1] : null;
}
