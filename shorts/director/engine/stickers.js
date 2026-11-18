// Thumbnail stickers: friendly reaction faces, arrows, hand-drawn rings, "?" badges and star bursts, drawn once on a canvas and placed
// on the overlay (full resolution, after tone mapping). Positions are fractions of the view: nx, ny in [-1, 1] from the centre, size is a
// fraction of the view's shorter side. Pure functions of the spec: no randomness, no time.
import * as THREE from 'three';

const INK = '#12141f';
function rr(c, x, y, w, h, r) { c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); }

function drawFace(c, S, mood, look) {
  const r = S * 0.46, cx = S / 2, cy = S / 2;
  c.save(); c.shadowColor = 'rgba(0,0,0,0.55)'; c.shadowBlur = S * 0.05; c.shadowOffsetY = S * 0.03;
  const g = c.createRadialGradient(cx - r * 0.3, cy - r * 0.35, r * 0.1, cx, cy, r); g.addColorStop(0, '#FFF2A6'); g.addColorStop(1, '#FFC93C');
  c.fillStyle = g; c.beginPath(); c.arc(cx, cy, r, 0, 6.2832); c.fill(); c.restore();
  c.lineWidth = S * 0.035; c.strokeStyle = INK; c.beginPath(); c.arc(cx, cy, r, 0, 6.2832); c.stroke();
  // cheeks
  c.fillStyle = 'rgba(255,120,120,0.45)'; [-1, 1].forEach(s => { c.beginPath(); c.ellipse(cx + s * r * 0.58, cy + r * 0.22, r * 0.14, r * 0.09, 0, 0, 6.2832); c.fill(); });
  // eyes: big white, pupils look toward `look` (-1 left .. 1 right)
  const ey = cy - r * 0.12, ex = r * 0.34, er = mood === 'surprised' ? r * 0.27 : r * 0.23;
  [-1, 1].forEach(s => {
    c.fillStyle = '#fff'; c.lineWidth = S * 0.025; c.strokeStyle = INK; c.beginPath(); c.ellipse(cx + s * ex, ey, er, er * 1.1, 0, 0, 6.2832); c.fill(); c.stroke();
    c.fillStyle = INK; c.beginPath(); c.arc(cx + s * ex + look * er * 0.42, ey + er * 0.1, er * 0.5, 0, 6.2832); c.fill();
    c.fillStyle = '#fff'; c.beginPath(); c.arc(cx + s * ex + look * er * 0.42 - er * 0.14, ey - er * 0.08, er * 0.16, 0, 6.2832); c.fill();
  });
  // brows
  c.lineWidth = S * 0.04; c.lineCap = 'round'; c.strokeStyle = INK;
  [-1, 1].forEach(s => { c.beginPath(); const by = ey - er * (mood === 'surprised' ? 1.65 : 1.45); c.moveTo(cx + s * ex - er * 0.8, by + (mood === 'curious' ? s * er * 0.25 : er * 0.15)); c.quadraticCurveTo(cx + s * ex, by - er * 0.35, cx + s * ex + er * 0.8, by + (mood === 'curious' ? -s * er * 0.1 : er * 0.15)); c.stroke(); });
  // mouth
  c.fillStyle = '#7a1f2b'; c.lineWidth = S * 0.03; c.strokeStyle = INK;
  if (mood === 'happy') { c.beginPath(); c.moveTo(cx - r * 0.38, cy + r * 0.3); c.quadraticCurveTo(cx, cy + r * 0.78, cx + r * 0.38, cy + r * 0.3); c.closePath(); c.fill(); c.stroke(); c.fillStyle = '#fff'; c.fillRect(cx - r * 0.26, cy + r * 0.3, r * 0.52, r * 0.1); }
  else if (mood === 'curious') { c.beginPath(); c.arc(cx + r * 0.05, cy + r * 0.52, r * 0.13, 0, 6.2832); c.fill(); c.stroke(); }
  else { c.beginPath(); c.ellipse(cx, cy + r * 0.5, r * 0.19, r * 0.27, 0, 0, 6.2832); c.fill(); c.stroke(); }   // surprised "O"
}

function drawArrow(c, W, H, color) {
  c.lineCap = 'round'; c.lineJoin = 'round';
  const path = () => { c.beginPath(); c.moveTo(W * 0.08, H * 0.78); c.bezierCurveTo(W * 0.3, H * 0.1, W * 0.62, H * 0.1, W * 0.84, H * 0.52); };
  const head = () => { c.beginPath(); c.moveTo(W * 0.66, H * 0.56); c.lineTo(W * 0.9, H * 0.58); c.lineTo(W * 0.8, H * 0.28); };
  c.shadowColor = 'rgba(0,0,0,0.5)'; c.shadowBlur = H * 0.06; c.shadowOffsetY = H * 0.03;
  c.strokeStyle = INK; c.lineWidth = H * 0.24; path(); c.stroke(); head(); c.stroke();
  c.shadowColor = 'transparent'; c.strokeStyle = color; c.lineWidth = H * 0.13; path(); c.stroke(); head(); c.stroke();
}

function drawRing(c, W, H, color) {   // a hand-drawn loop around the subject
  c.lineCap = 'round'; c.lineJoin = 'round';
  const loop = () => { c.beginPath(); for (let i = 0; i <= 64; i++) { const a = i / 64 * 6.2832 * 1.08 - 0.5, w = 1 + 0.035 * Math.sin(a * 3), x = W / 2 + Math.cos(a) * W * 0.44 * w, y = H / 2 + Math.sin(a) * H * 0.44 * w; i ? c.lineTo(x, y) : c.moveTo(x, y); } };
  c.shadowColor = 'rgba(0,0,0,0.5)'; c.shadowBlur = H * 0.04; c.strokeStyle = INK; c.lineWidth = H * 0.085; loop(); c.stroke();
  c.shadowColor = 'transparent'; c.strokeStyle = color; c.lineWidth = H * 0.05; loop(); c.stroke();
}

function drawQ(c, S, color, text) {
  c.textAlign = 'center'; c.textBaseline = 'middle'; c.font = `900 ${S * 0.95}px "Inter", sans-serif`;
  c.lineJoin = 'round'; c.lineWidth = S * 0.16; c.strokeStyle = INK; c.shadowColor = 'rgba(0,0,0,0.5)'; c.shadowBlur = S * 0.06; c.shadowOffsetY = S * 0.04;
  c.strokeText(text, S / 2, S * 0.54); c.shadowColor = 'transparent'; const g = c.createLinearGradient(0, S * 0.1, 0, S * 0.9); g.addColorStop(0, '#FFFFFF'); g.addColorStop(1, color);
  c.fillStyle = g; c.fillText(text, S / 2, S * 0.54);
}

function drawBurst(c, S, color, text) {   // a star-shaped badge with a short word
  const n = 14, cx = S / 2, cy = S / 2;
  c.save(); c.shadowColor = 'rgba(0,0,0,0.5)'; c.shadowBlur = S * 0.05; c.shadowOffsetY = S * 0.03; c.beginPath();
  for (let i = 0; i < n * 2; i++) { const a = i / (n * 2) * 6.2832, r = (i % 2 ? 0.37 : 0.49) * S; i ? c.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r) : c.moveTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r); }
  c.closePath(); c.fillStyle = color; c.fill(); c.restore(); c.lineJoin = 'round'; c.lineWidth = S * 0.03; c.strokeStyle = INK; c.stroke();
  c.fillStyle = INK; c.textAlign = 'center'; c.textBaseline = 'middle'; c.font = `900 ${S * 0.2}px "Inter","Noto Sans Devanagari",sans-serif`; c.fillText(text, cx, cy);
}

export class Sticker {
  constructor(spec, ctx) {
    const view = ctx.view, shortSide = Math.min(view.w, view.h), size = spec.size * shortSide;
    const aspect = spec.type === 'arrow' ? 1.6 : 1;
    this.canvas = document.createElement('canvas'); const S = 512; this.canvas.width = S * aspect | 0; this.canvas.height = S; const c = this.canvas.getContext('2d');
    const color = spec.color || '#FFCC33';
    if (spec.type === 'face') drawFace(c, S, spec.mood || 'surprised', spec.look ?? 0.8);
    else if (spec.type === 'arrow') drawArrow(c, this.canvas.width, S, color);
    else if (spec.type === 'ring') drawRing(c, this.canvas.width, S, color);
    else if (spec.type === 'qmark') drawQ(c, S, color, spec.text || '?');
    else if (spec.type === 'burst') drawBurst(c, S, color, spec.text || 'NEW');
    const tex = new THREE.CanvasTexture(this.canvas); tex.colorSpace = THREE.SRGBColorSpace; tex.minFilter = THREE.LinearFilter; tex.generateMipmaps = false;
    this.mesh = new THREE.Mesh(new THREE.PlaneGeometry(size * aspect, size), new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthTest: false, depthWrite: false, toneMapped: false }));
    this.mesh.renderOrder = spec.type === 'ring' ? 15 : 30;   // a ring sits behind the headline, faces and badges in front
    this.mesh.position.set(spec.nx * view.w / 2, spec.ny * view.h / 2, -ctx.dist);
    this.mesh.rotation.z = THREE.MathUtils.degToRad(spec.tilt || 0);
    if (spec.flip) this.mesh.scale.x = -1;
  }
  dispose() { this.mesh.material.map.dispose(); this.mesh.material.dispose(); this.mesh.geometry.dispose(); }
}
