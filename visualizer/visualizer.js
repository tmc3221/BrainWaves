// visualizer.js
// Renderer process script for BrainWaves Neon Visualizer

const { ipcRenderer } = require('electron');

/** ---------------------------
 *  DOM bootstrap
 *  ---------------------------
 */
const root = document.body;
root.style.margin = '0';
root.style.overflow = 'hidden';
root.style.background = '#000';

const statusBar = document.createElement('div');
statusBar.style.position = 'fixed';
statusBar.style.left = '12px';
statusBar.style.bottom = '12px';
statusBar.style.padding = '6px 10px';
statusBar.style.fontFamily = 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace';
statusBar.style.fontSize = '12px';
statusBar.style.color = '#9ae6b4';
statusBar.style.background = 'rgba(0,0,0,0.35)';
statusBar.style.border = '1px solid rgba(255,255,255,0.08)';
statusBar.style.borderRadius = '8px';
statusBar.style.pointerEvents = 'none';
statusBar.textContent = 'Waiting for video…';
root.appendChild(statusBar);

const canvas = document.createElement('canvas');
canvas.id = 'neon-canvas';
canvas.style.position = 'fixed';
canvas.style.left = 0;
canvas.style.top = 0;
canvas.style.width = '100vw';
canvas.style.height = '100vh';
canvas.style.display = 'block';
root.appendChild(canvas);

const video = document.createElement('video');
video.id = 'video';
video.style.position = 'fixed';
video.style.left = 0;
video.style.top = 0;
video.style.width = '100vw';
video.style.height = '100vh';
video.style.objectFit = 'cover';
video.style.opacity = '0.35'; // let neon show through
video.muted = true;           // allow autoplay
video.playsInline = true;
video.controls = false;
video.autoplay = true;
video.crossOrigin = 'anonymous'; // needed for WebAudio if CORS allows
root.appendChild(video);

// Toggle mute on click
root.addEventListener('click', () => {
  // Try unmuting on user gesture
  if (video.muted) video.muted = false;
});

/** ---------------------------
 *  Utils
 *  ---------------------------
 */
function setStatus(msg, color = '#9ae6b4') {
  statusBar.textContent = msg;
  statusBar.style.color = color;
}

function getQueryParam(name) {
  const u = new URL(window.location.href);
  return u.searchParams.get(name);
}

/** ---------------------------
 *  Resolve video URL and request stream URL
 *  ---------------------------
 */
async function resolveVideoToStreamUrl() {
  let youtubeUrl = getQueryParam('video');

  if (!youtubeUrl) {
    // ask main if it got one from argv
    youtubeUrl = await new Promise((resolve) => {
      ipcRenderer.once('video-url', (_evt, url) => resolve(url || null));
      ipcRenderer.send('get-video-url');
    });
  }

  if (!youtubeUrl) {
    throw new Error('No YouTube URL provided.');
  }

  setStatus('Requesting stream URL…');

  const res = await ipcRenderer.invoke('get-video-stream-url', youtubeUrl);
  if (!res || !res.success || !res.streamUrl) {
    const err = res && res.error ? res.error : 'Unknown stream resolution error.';
    throw new Error(err);
  }

  return {
    streamUrl: res.streamUrl,
    title: res.title || 'YouTube',
    duration: res.duration ? Number(res.duration) : null,
    youtubeUrl
  };
}

/** ---------------------------
 *  WebAudio + Neon Visualizer
 *  ---------------------------
 */
let rafId = null;

function startNeonVisualizerFor(videoEl) {
  const ctx = canvas.getContext('2d', { alpha: false });

  function resize() {
    // Cap DPR at 1.5 to avoid excessive rendering on high-DPI displays
    // This significantly improves performance on 2x/3x displays
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    const w = Math.floor(window.innerWidth * dpr);
    const h = Math.floor(window.innerHeight * dpr);
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
    }
  }
  resize();
  window.addEventListener('resize', resize);

  const AudioCtx = window.AudioContext || window.webkitAudioContext;
  const audioCtx = new AudioCtx();

  // Create source & analyser
  const source = audioCtx.createMediaElementSource(videoEl);
  const analyser = audioCtx.createAnalyser();

  // FFT size controls number of bars; 2048→1024 bins; we’ll sample fewer
  analyser.fftSize = 2048;
  analyser.smoothingTimeConstant = 0.85;

  source.connect(analyser);
  // Still route to destination so the user hears audio
  analyser.connect(audioCtx.destination);

  const freq = new Uint8Array(analyser.frequencyBinCount);

  // Visual params
  const BAR_GROUPS = 96;         // number of bars
  const GLOW_PASSES = 1;         // reduced from 2 for better performance
  const BASE_HUE = 170;          // teal/blue base; we’ll oscillate
  const HUE_SWAY = 55;           // color sway around base
  const ROUND = 12;              // bar corner radius in px (at 1x)
  const FLOOR = 0.08;            // minimum bar height as a fraction of screen
  const EXP = 1.28;              // emphasize mids with exponent
  const CAP_DECAY = 0.02;        // decay speed for peak caps

  // Peak caps (like classic spectrum analyzers)
  const caps = new Float32Array(BAR_GROUPS).fill(0);

  function drawFrame() {
    rafId = requestAnimationFrame(drawFrame);

    analyser.getByteFrequencyData(freq);

    const w = canvas.width;
    const h = canvas.height;

    // Background radial gradient
    const g = ctx.createRadialGradient(
      w * 0.5, h * 0.5, Math.min(w, h) * 0.1,
      w * 0.5, h * 0.5, Math.max(w, h) * 0.7
    );
    g.addColorStop(0, '#000000');
    g.addColorStop(1, '#000000');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);

    // Compute bars from frequency bins (log-ish sampling)
    const bins = freq.length;
    const bars = BAR_GROUPS;
    const barW = (w / bars) * 0.75;
    const gap = (w / bars) * 0.25;

    // Color pulse over time with audio energy
    let energy = 0;
    for (let i = 0; i < bins; i++) energy += freq[i];
    energy /= (bins * 255);
    const t = performance.now() * 0.001;
    const hue = BASE_HUE + Math.sin(t * 0.75 + energy * 2.5) * HUE_SWAY;
    const neon = `hsl(${hue.toFixed(1)}, 95%, 60%)`;
    const neonDim = `hsla(${hue.toFixed(1)}, 95%, 60%, 0.4)`;

    // Overglow
    ctx.globalCompositeOperation = 'screen';

    for (let pass = 0; pass < GLOW_PASSES; pass++) {
      const blur = Math.floor(Math.max(w, h) * (pass ? 0.02 : 0.01));
      ctx.filter = `blur(${blur}px)`;
      ctx.fillStyle = pass ? neonDim : neon;

      let x = 0;
      for (let i = 0; i < bars; i++) {
        // Map i→log bin index
        const fIdx = Math.floor(Math.pow(i / (bars - 1), 1.35) * (bins - 1));
        const v = freq[fIdx] / 255;

        // Shape curve to emphasize mids
        const shaped = Math.pow(v, EXP);

        const minH = h * FLOOR;
        const barH = Math.max(minH, shaped * (h * 0.9));

        // Peak caps
        caps[i] = Math.max(caps[i] - h * CAP_DECAY, barH);
        const y = h - barH;

        // Rounded rect bars (use capped DPR for consistency)
        const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
        roundRect(ctx, x, y, barW, barH, ROUND * dpr);
        ctx.fill();

        // Peak cap small rectangles
        const capH = Math.max(6 * dpr, barW * 0.18);
        roundRect(ctx, x, h - caps[i] - capH, barW, capH, ROUND * 0.8 * dpr);
        ctx.fill();

        x += barW + gap;
      }
    }

    // Foreground crisp bars (no blur)
    ctx.filter = 'none';
    ctx.fillStyle = neon;
    let x = 0;
    for (let i = 0; i < bars; i++) {
      const fIdx = Math.floor(Math.pow(i / (bars - 1), 1.35) * (bins - 1));
      const v = freq[fIdx] / 255;
      const shaped = Math.pow(v, EXP);
      const minH = h * FLOOR;
      const barH = Math.max(minH, shaped * (h * 0.9));
      const y = h - barH;

      const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      roundRect(ctx, x, y, barW, barH, ROUND * dpr);
      ctx.fill();

      x += barW + gap;
    }

    ctx.globalCompositeOperation = 'source-over';
  }

  // Kick audio after first user gesture if autoplay blocks audio context
  const resumeAudio = async () => {
    try {
      if (audioCtx.state === 'suspended') {
        await audioCtx.resume();
      }
    } catch {}
  };
  window.addEventListener('click', resumeAudio, { once: true });
  window.addEventListener('keydown', resumeAudio, { once: true });

  drawFrame();

  return () => {
    window.removeEventListener('resize', resize);
    if (rafId) cancelAnimationFrame(rafId);
    try { source.disconnect(); } catch {}
    try { analyser.disconnect(); } catch {}
    try { audioCtx.close(); } catch {}
  };
}

function roundRect(ctx, x, y, w, h, r) {
  const rr = Math.min(r, Math.min(w, h) * 0.5);
  ctx.beginPath();
  ctx.moveTo(x + rr, y);
  ctx.lineTo(x + w - rr, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + rr);
  ctx.lineTo(x + w, y + h - rr);
  ctx.quadraticCurveTo(x + w, y + h, x + w - rr, y + h);
  ctx.lineTo(x + rr, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - rr);
  ctx.lineTo(x, y + rr);
  ctx.quadraticCurveTo(x, y, x + rr, y);
  ctx.closePath();
}

/** ---------------------------
 *  Boot
 *  ---------------------------
 */
(async function boot() {
  try {
    setStatus('Resolving video…');

    const { streamUrl, title, duration, youtubeUrl } = await resolveVideoToStreamUrl();

    // Prefer direct stream; if it fails, fallback to YouTube page URL (non-analyzable)
    const src = streamUrl || youtubeUrl;

    // Some direct links require referrer; Electron usually forwards it fine.
    // Set source and play
    video.src = src;

    // Attempt to start (muted)
    await video.play().catch(() => { /* ignore, gesture may be required */ });

    // Title feedback
    const durText = duration ? ` • ${Math.round(duration / 60)}m` : '';
    setStatus(`Playing: ${title}${durText}`);

    // Start visualizer
    startNeonVisualizerFor(video);

  } catch (err) {
    console.error(err);
    setStatus(`Error: ${err.message}`, '#fca5a5');
    // Last resort: display a message and leave canvas background as-is
  }
})();

