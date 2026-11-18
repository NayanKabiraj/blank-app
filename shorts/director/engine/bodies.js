// Procedural planets for thumbnails: a cratered Moon, an Earth with continents and clouds, a boiling Sun. Textures are drawn on a canvas
// from a seeded RNG (no assets, deterministic) and wrapped on a sphere.
import * as THREE from 'three';
import { mulberry32 } from './util.js';

function blob(g, x, y, r, rng, color, n = 9, wob = 0.35) {
  g.beginPath();
  for (let i = 0; i <= n; i++) { const a = i / n * 6.2832, rr = r * (1 + (rng() - 0.5) * wob * 2); const px = x + Math.cos(a) * rr, py = y + Math.sin(a) * rr * 0.8; i ? g.lineTo(px, py) : g.moveTo(px, py); }
  g.closePath(); g.fillStyle = color; g.fill();
}

export function bodyTexture(kind, seed) {
  const W = 1024, H = 512, cv = document.createElement('canvas'); cv.width = W; cv.height = H; const g = cv.getContext('2d'), rng = mulberry32(seed + 77);
  if (kind === 'moon') {
    g.fillStyle = '#b9b9c2'; g.fillRect(0, 0, W, H);
    for (let i = 0; i < 70; i++) { blob(g, rng() * W, rng() * H, 40 + rng() * 90, rng, `rgba(${110 + rng() * 40 | 0},${110 + rng() * 40 | 0},${120 + rng() * 40 | 0},0.35)`, 12, 0.4); }   // maria
    for (let i = 0; i < 260; i++) {
      const x = rng() * W, y = rng() * H, r = 4 + rng() * rng() * 38;
      const gr = g.createRadialGradient(x - r * 0.25, y - r * 0.25, r * 0.1, x, y, r); gr.addColorStop(0, 'rgba(70,70,82,0.55)'); gr.addColorStop(0.85, 'rgba(95,95,108,0.45)'); gr.addColorStop(1, 'rgba(235,235,245,0.55)');
      g.fillStyle = gr; g.beginPath(); g.arc(x, y, r, 0, 6.2832); g.fill();
    }
  } else if (kind === 'earth') {
    const sea = g.createLinearGradient(0, 0, 0, H); sea.addColorStop(0, '#2a7fff'); sea.addColorStop(0.5, '#0a4fd6'); sea.addColorStop(1, '#2a7fff'); g.fillStyle = sea; g.fillRect(0, 0, W, H);
    for (let i = 0; i < 22; i++) { const x = rng() * W, y = H * (0.18 + rng() * 0.64), r = 40 + rng() * 90; blob(g, x, y, r, rng, '#2fb457', 14, 0.5); blob(g, x + r * 0.2, y + r * 0.1, r * 0.55, rng, '#a8883a', 10, 0.5); }
    g.fillStyle = '#f4f8ff'; g.fillRect(0, 0, W, 26); g.fillRect(0, H - 26, W, 26);   // ice caps
    for (let i = 0; i < 40; i++) blob(g, rng() * W, rng() * H, 24 + rng() * 60, rng, 'rgba(255,255,255,0.55)', 10, 0.6);   // clouds
  } else {   // sun
    const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#ffb300'); gr.addColorStop(0.5, '#ffd84a'); gr.addColorStop(1, '#ffb300'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
    for (let i = 0; i < 520; i++) { const x = rng() * W, y = rng() * H, r = 6 + rng() * 26; g.fillStyle = rng() > 0.5 ? 'rgba(255,120,0,0.22)' : 'rgba(255,255,200,0.28)'; g.beginPath(); g.arc(x, y, r, 0, 6.2832); g.fill(); }
  }
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.wrapS = THREE.RepeatWrapping; return tex;
}

export function bodyMaterial(kind, seed) {
  const map = bodyTexture(kind, seed);
  if (kind === 'sun') return new THREE.MeshBasicMaterial({ map, color: new THREE.Color(1.5, 1.25, 0.9), toneMapped: false });
  return new THREE.MeshStandardMaterial({ map, roughness: kind === 'moon' ? 0.95 : 0.6, metalness: 0, emissive: new THREE.Color(kind === 'earth' ? '#06204a' : '#1a1a22'), emissiveIntensity: 0.55 });
}
