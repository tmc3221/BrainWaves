/**
 * BrainWaves Neon Visualizer - Electron Main Process
 * 
 * Handles window creation and app lifecycle
 */

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const url = require('url');

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
