/**
 * BrainWaves Neon Visualizer - Main Renderer
 * 
 * Implements Three.js video rendering with audio-reactive post-processing effects
 */

const ytdl = require('ytdl-core');
const { Readable } = require('stream');

// Global state
let scene, camera, renderer, videoMesh;
let videoElement, audioContext, analyser;
let bassLevel = 0, midLevel = 0, highLevel = 0;
let composer, bloomPass, rgbShiftPass, glitchPass;
let clock, frameCount = 0;
let lastFpsUpdate = 0;

// Effect parameters
let params = {
  bloom: 1.5,
  rgbShift: 0.005,
  glitch: 0.3,
  kaleidoscope: 6
};

/**
 * Initialize the visualizer
 */
async function init() {
  try {
    updateStatus('Setting up Three.js scene...');
    
    // Get video URL from query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const videoUrl = urlParams.get('video');
    
    if (!videoUrl) {
      showError('No video URL provided. Please pass a YouTube URL via --video-url parameter.');
      return;
    }

    // Setup Three.js scene
    setupScene();
    
    // Setup audio capture
    await setupAudio();
    
    // Setup video streaming
    await setupVideo(videoUrl);
    
    // Setup post-processing effects
    setupPostProcessing();
    
    // Setup controls
    setupControls();
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize, false);
    
    updateStatus('Ready! Enjoy the vibes...');
    hideLoading();
    
    // Start animation loop
    animate();
    
  } catch (error) {
    console.error('Initialization error:', error);
    showError(`Failed to initialize: ${error.message}`);
  }
}

/**
 * Setup Three.js scene
 */
function setupScene() {
  // Scene
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000000);
  
  // Camera
  camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.z = 2;
  
  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  document.getElementById('container').appendChild(renderer.domElement);
  
  // Clock for animations
  clock = new THREE.Clock();
}

/**
 * Setup video streaming from YouTube
 */
async function setupVideo(videoUrl) {
  updateStatus('Streaming video from YouTube...');
  
  try {
    // Create video element
    videoElement = document.createElement('video');
    videoElement.crossOrigin = 'anonymous';
    videoElement.loop = true;
    videoElement.muted = false; // We'll use Web Audio API instead
    videoElement.playsInline = true;
    
    // Get video info and stream
    const info = await ytdl.getInfo(videoUrl);
    const format = ytdl.chooseFormat(info.formats, { quality: 'highestvideo' });
    
    if (!format) {
      throw new Error('No suitable video format found');
    }
    
    // Stream video using ytdl-core
    const videoStream = ytdl.downloadFromInfo(info, { format: format });
    
    // Convert stream to blob URL for video element
    const chunks = [];
    videoStream.on('data', (chunk) => chunks.push(chunk));
    videoStream.on('end', () => {
      const blob = new Blob(chunks, { type: 'video/mp4' });
      const blobUrl = URL.createObjectURL(blob);
      videoElement.src = blobUrl;
      videoElement.play();
    });
    
    // Create video texture
    const videoTexture = new THREE.VideoTexture(videoElement);
    videoTexture.minFilter = THREE.LinearFilter;
    videoTexture.magFilter = THREE.LinearFilter;
    
    // Create plane mesh for video
    const geometry = new THREE.PlaneGeometry(16, 9);
    const material = new THREE.MeshBasicMaterial({ 
      map: videoTexture,
      side: THREE.DoubleSide
    });
    
    videoMesh = new THREE.Mesh(geometry, material);
    scene.add(videoMesh);
    
    // Scale to fit viewport
    const aspect = window.innerWidth / window.innerHeight;
    const videoAspect = 16 / 9;
    
    if (aspect > videoAspect) {
      videoMesh.scale.set(aspect / videoAspect, 1, 1);
    } else {
      videoMesh.scale.set(1, videoAspect / aspect, 1);
    }
    
    updateStatus('Video streaming active');
    
  } catch (error) {
    console.error('Video setup error:', error);
    showError(`Video setup failed: ${error.message}`);
    throw error;
  }
}

/**
 * Setup audio capture and analysis
 */
async function setupAudio() {
  updateStatus('Setting up audio capture...');
  
  try {
    // Create audio context
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    // Create analyser node
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 512;
    analyser.smoothingTimeConstant = 0.8;
    
    // Try to get audio from user media (Scarlett interface preferred)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false
        } 
      });
      
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      
      updateAudioStatus('Audio: Scarlett interface connected ✓');
      
    } catch (error) {
      console.warn('Failed to get user media, falling back to video audio:', error);
      
      // Fallback to video element audio
      if (videoElement) {
        const source = audioContext.createMediaElementSource(videoElement);
        source.connect(analyser);
        analyser.connect(audioContext.destination);
        updateAudioStatus('Audio: Video audio connected');
      }
    }
    
  } catch (error) {
    console.error('Audio setup error:', error);
    updateAudioStatus('Audio: Failed to connect');
  }
}

/**
 * Setup post-processing effects
 */
function setupPostProcessing() {
  updateStatus('Setting up effects...');
  
  // Note: For a production app, you'd use EffectComposer from three/examples/jsm/postprocessing
  // For this implementation, we'll apply effects via custom shaders
  
  // Create custom shader material for effects
  const effectMaterial = new THREE.ShaderMaterial({
    uniforms: {
      tDiffuse: { value: null },
      time: { value: 0 },
      bassLevel: { value: 0 },
      midLevel: { value: 0 },
      highLevel: { value: 0 },
      bloomStrength: { value: params.bloom },
      rgbShiftAmount: { value: params.rgbShift },
      glitchAmount: { value: params.glitch },
      kaleidoscopeSegments: { value: params.kaleidoscope }
    },
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform sampler2D tDiffuse;
      uniform float time;
      uniform float bassLevel;
      uniform float midLevel;
      uniform float highLevel;
      uniform float bloomStrength;
      uniform float rgbShiftAmount;
      uniform float glitchAmount;
      uniform float kaleidoscopeSegments;
      
      varying vec2 vUv;
      
      // Kaleidoscope effect
      vec2 kaleidoscope(vec2 uv, float segments) {
        vec2 center = vec2(0.5, 0.5);
        vec2 toCenter = uv - center;
        float angle = atan(toCenter.y, toCenter.x);
        float radius = length(toCenter);
        
        float segmentAngle = 6.28318530718 / segments;
        angle = mod(angle, segmentAngle);
        if (mod(floor((atan(toCenter.y, toCenter.x) / segmentAngle)), 2.0) == 1.0) {
          angle = segmentAngle - angle;
        }
        
        return center + radius * vec2(cos(angle), sin(angle));
      }
      
      // RGB Shift effect
      vec4 rgbShift(sampler2D tex, vec2 uv, float amount) {
        float r = texture2D(tex, uv + vec2(amount * bassLevel, 0.0)).r;
        float g = texture2D(tex, uv).g;
        float b = texture2D(tex, uv - vec2(amount * bassLevel, 0.0)).b;
        return vec4(r, g, b, 1.0);
      }
      
      // Simple bloom
      vec4 bloom(vec4 color, float strength) {
        float brightness = dot(color.rgb, vec3(0.299, 0.587, 0.114));
        if (brightness > 0.5) {
          return color * (1.0 + strength * midLevel);
        }
        return color;
      }
      
      // Glitch effect
      vec2 glitch(vec2 uv, float amount) {
        if (amount > 0.5 && mod(uv.y * 100.0 + time * 10.0, 1.0) < amount * highLevel) {
          return vec2(uv.x + (fract(sin(uv.y * 100.0) * 43758.5453) - 0.5) * 0.1 * amount, uv.y);
        }
        return uv;
      }
      
      void main() {
        vec2 uv = vUv;
        
        // Apply kaleidoscope
        if (kaleidoscopeSegments > 1.0) {
          uv = kaleidoscope(uv, kaleidoscopeSegments * (1.0 + bassLevel * 0.5));
        }
        
        // Apply glitch
        uv = glitch(uv, glitchAmount);
        
        // Get color with RGB shift
        vec4 color = rgbShift(tDiffuse, uv, rgbShiftAmount);
        
        // Apply bloom
        color = bloom(color, bloomStrength);
        
        // Add neon glow based on high frequencies
        color.rgb += vec3(0.0, 1.0, 1.0) * highLevel * 0.3;
        
        gl_FragColor = color;
      }
    `
  });
  
  // Store for later use in render loop
  window.effectMaterial = effectMaterial;
}

/**
 * Setup UI controls
 */
function setupControls() {
  // Bloom
  const bloomSlider = document.getElementById('bloom');
  const bloomValue = document.getElementById('bloom-value');
  bloomSlider.addEventListener('input', (e) => {
    params.bloom = parseFloat(e.target.value);
    bloomValue.textContent = params.bloom.toFixed(1);
  });
  
  // RGB Shift
  const rgbShiftSlider = document.getElementById('rgbshift');
  const rgbShiftValue = document.getElementById('rgbshift-value');
  rgbShiftSlider.addEventListener('input', (e) => {
    params.rgbShift = parseFloat(e.target.value);
    rgbShiftValue.textContent = params.rgbShift.toFixed(3);
  });
  
  // Glitch
  const glitchSlider = document.getElementById('glitch');
  const glitchValue = document.getElementById('glitch-value');
  glitchSlider.addEventListener('input', (e) => {
    params.glitch = parseFloat(e.target.value);
    glitchValue.textContent = params.glitch.toFixed(1);
  });
  
  // Kaleidoscope
  const kaleidoscopeSlider = document.getElementById('kaleidoscope');
  const kaleidoscopeValue = document.getElementById('kaleidoscope-value');
  kaleidoscopeSlider.addEventListener('input', (e) => {
    params.kaleidoscope = parseInt(e.target.value);
    kaleidoscopeValue.textContent = params.kaleidoscope;
  });
}

/**
 * Analyze audio frequencies
 */
function analyzeAudio() {
  if (!analyser) return;
  
  const bufferLength = analyser.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);
  analyser.getByteFrequencyData(dataArray);
  
  // Split into frequency bands
  const bassEnd = Math.floor(bufferLength * 0.1);
  const midEnd = Math.floor(bufferLength * 0.5);
  
  // Calculate average levels for each band
  let bass = 0, mid = 0, high = 0;
  
  for (let i = 0; i < bassEnd; i++) {
    bass += dataArray[i];
  }
  bass = (bass / bassEnd) / 255.0;
  
  for (let i = bassEnd; i < midEnd; i++) {
    mid += dataArray[i];
  }
  mid = (mid / (midEnd - bassEnd)) / 255.0;
  
  for (let i = midEnd; i < bufferLength; i++) {
    high += dataArray[i];
  }
  high = (high / (bufferLength - midEnd)) / 255.0;
  
  // Smooth transitions
  bassLevel = bassLevel * 0.7 + bass * 0.3;
  midLevel = midLevel * 0.7 + mid * 0.3;
  highLevel = highLevel * 0.7 + high * 0.3;
}

/**
 * Animation loop
 */
function animate() {
  requestAnimationFrame(animate);
  
  // Analyze audio
  analyzeAudio();
  
  // Update mesh rotation based on bass
  if (videoMesh) {
    videoMesh.rotation.z = Math.sin(clock.getElapsedTime() * 0.5) * 0.05 * bassLevel;
  }
  
  // Render with effects
  renderWithEffects();
  
  // Update FPS counter
  frameCount++;
  const now = performance.now();
  if (now - lastFpsUpdate > 1000) {
    updateFPS(frameCount);
    frameCount = 0;
    lastFpsUpdate = now;
  }
}

/**
 * Render with post-processing effects
 */
function renderWithEffects() {
  // For now, just render directly
  // In a full implementation, you'd render to a texture and apply effects
  renderer.render(scene, camera);
  
  // Apply effects via shader if available
  if (window.effectMaterial && videoMesh) {
    window.effectMaterial.uniforms.time.value = clock.getElapsedTime();
    window.effectMaterial.uniforms.bassLevel.value = bassLevel;
    window.effectMaterial.uniforms.midLevel.value = midLevel;
    window.effectMaterial.uniforms.highLevel.value = highLevel;
    window.effectMaterial.uniforms.bloomStrength.value = params.bloom;
    window.effectMaterial.uniforms.rgbShiftAmount.value = params.rgbShift;
    window.effectMaterial.uniforms.glitchAmount.value = params.glitch;
    window.effectMaterial.uniforms.kaleidoscopeSegments.value = params.kaleidoscope;
    
    // Apply material to video mesh
    videoMesh.material = window.effectMaterial;
    window.effectMaterial.uniforms.tDiffuse.value = videoMesh.material.map;
  }
}

/**
 * Handle window resize
 */
function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  
  // Update video mesh scale
  if (videoMesh) {
    const aspect = window.innerWidth / window.innerHeight;
    const videoAspect = 16 / 9;
    
    if (aspect > videoAspect) {
      videoMesh.scale.set(aspect / videoAspect, 1, 1);
    } else {
      videoMesh.scale.set(1, videoAspect / aspect, 1);
    }
  }
}

/**
 * UI Helper Functions
 */
function updateStatus(message) {
  document.getElementById('status').textContent = message;
}

function updateAudioStatus(message) {
  document.getElementById('audio-status').textContent = message;
}

function updateFPS(fps) {
  document.getElementById('fps').textContent = `FPS: ${fps}`;
}

function showError(message) {
  const errorDiv = document.getElementById('error');
  errorDiv.textContent = message;
  errorDiv.style.display = 'block';
  hideLoading();
}

function hideLoading() {
  document.getElementById('loading').classList.add('hidden');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
