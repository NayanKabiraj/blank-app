// 2D cartoon explainer scene in a "traditional animation" look, rendered frame by frame by
// ../cartoon3d/render.cjs. Everything is drawn by code: a softly painted background chosen
// by niche, an original presenter character (full colour, warm brown outlines, flat cel
// shading, big expressive face that talks while the narration plays), the scene's subject
// inside a round "thought bubble" inset, and parchment text cards.
// Everything is a pure function of time t (no Math.random, Date or CSS animation), so the
// render can be split across parallel browsers. Text is HTML so Devanagari is shaped correctly.

const W = 1080, H = 1920, INTRO = 0.6, OUTRO = 0.35, GROUND = 1255;
const INK = '#3b2a20';
// [accent, accent2, soft bubble tint]
const PALETTES = [
  ['#d9534f', '#2f80b7', '#fde9c9'],
  ['#2f9e8f', '#e07a3f', '#e3f4ef'],
  ['#2f80b7', '#e9a23b', '#e4f0fa'],
  ['#e07a3f', '#7b5ea7', '#fdeedd'],
  ['#7b5ea7', '#2f9e8f', '#efe8f7'],
  ['#c0392b', '#2f9e8f', '#fff2c6'],
];
// the presenter: fixed look so the channel has one recognisable character
const SKIN = '#e9b48d', SKIN_SH = '#d39a74', HAIR = '#4a2f22', SHIRT = '#3f8fc0', SHIRT_SH = '#2f739d',
      COLLAR = '#f2e6cf', PANTS = '#6d5140', SHOE = '#3f2a1f';

const BACKDROP = {
  'How Tech Works': 'room', 'AI Explained': 'room', 'Science Explained': 'room', 'Human Body': 'room',
  'Brain & Psychology': 'room', 'Money Explained': 'town', "How It's Made": 'town',
  'Engineering Marvels': 'town', 'Earth & Nature': 'nature', 'Space & Universe': 'space',
  'History of Ideas': 'classical',
};

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
// Measured motion (SousekiL/vox-style-video, MIT, style/collage-motion 05-motion and 06-transitions):
// prop pop-in per 12 fps step (+28 % peak), stamp spring per frame, whip-pan offsets in % of width.
const POP = [0.28, 0.81, 1.21, 1.28, 1.17, 1.07, 1.0, 0.98, 1.0];
const STAMP = [0.78, 1.26, 1.15, 0.95, 0.92, 0.97, 1.0];
const WHIP_OUT = [-0.18, -0.10, -0.025, -0.006, 0];        // last 5 drawings before a cut (index = drawings left)
const popAt = dt => (dt < 0 ? 0 : POP[Math.min(POP.length - 1, Math.floor(dt * 12))]);
const stampAt = dt => (dt < 0 ? 1 : STAMP[Math.min(STAMP.length - 1, Math.floor(dt * 30))]);
const expoOut = x => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x));
const ATTN = '#FFF200';                                     // the one attention colour: highlighter yellow
const lerp = (a, b, k) => a + (b - a) * k;
const easeOutBack = x => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const easeOutCubic = x => 1 - Math.pow(1 - x, 3);
const easeInOut = x => (x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2);
const hash = s => { let h = 7; for (const c of s) h = (h * 31 + c.charCodeAt(0)) >>> 0; return h; };
const rnd = n => { const x = Math.sin(n * 12.9898 + 78.233) * 43758.5453; return x - Math.floor(x); };

let cfg, pal, ctx, bg, clouds, segs = [], T = 0, strokeId = 0, kindOfBg = 'room';
const segsPhoto = {}, segsBg = {}, segsKind = {};

// ------------------------------------------------------------------ pen: clean ink strokes
// pts: [[x,y],...]. o: {close, w, color, fill, p (draw-on progress 0..1), amp}
function pen(pts, o = {}) {
  const p = o.p ?? 1, id = strokeId++;
  if (p <= 0 || pts.length < 2) return;
  const amp = o.amp ?? 0.6;
  const src = o.close ? [...pts, pts[0]] : pts;
  const out = [];
  let k = 0;
  for (let i = 0; i < src.length - 1; i++) {
    const [x1, y1] = src[i], [x2, y2] = src[i + 1];
    const len = Math.hypot(x2 - x1, y2 - y1), n = Math.max(1, Math.round(len / 18));
    const nx = -(y2 - y1) / (len || 1), ny = (x2 - x1) / (len || 1);
    for (let j = 0; j < n; j++, k++) {
      const f = j / n, d = (rnd(id * 131 + k * 7) - 0.5) * 2 * amp;
      out.push([x1 + (x2 - x1) * f + nx * d, y1 + (y2 - y1) * f + ny * d]);
    }
  }
  const last = src[src.length - 1];
  out.push(o.close ? out[0] : [last[0], last[1]]);
  if (o.fill) {
    ctx.save(); ctx.globalAlpha *= clamp(p * 1.6 - 0.3); ctx.fillStyle = o.fill;
    ctx.beginPath(); out.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.fill(); ctx.restore();
  }
  let total = 0; const seg = [];
  for (let i = 1; i < out.length; i++) { const l = Math.hypot(out[i][0] - out[i - 1][0], out[i][1] - out[i - 1][1]); seg.push(l); total += l; }
  let budget = total * clamp(p);
  ctx.strokeStyle = o.color || INK; ctx.lineWidth = o.w ?? 6; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(out[0][0], out[0][1]);
  for (let i = 1; i < out.length && budget > 0; i++) {
    const l = seg[i - 1];
    if (l <= budget) ctx.lineTo(out[i][0], out[i][1]);
    else { const f = budget / l; ctx.lineTo(lerp(out[i - 1][0], out[i][0], f), lerp(out[i - 1][1], out[i][1], f)); }
    budget -= l;
  }
  ctx.stroke();
}
const arcPts = (cx, cy, rx, ry, a0 = 0, a1 = Math.PI * 2, n = 32, rot = 0) => Array.from({ length: n + 1 }, (_, i) => {
  const a = a0 + (a1 - a0) * (i / n), x = Math.cos(a) * rx, y = Math.sin(a) * ry;
  return [cx + x * Math.cos(rot) - y * Math.sin(rot), cy + x * Math.sin(rot) + y * Math.cos(rot)];
});
const circle = (cx, cy, r, o = {}) => pen(arcPts(cx, cy, r, r, 0, Math.PI * 2, Math.max(16, Math.round(r / 3))).slice(0, -1), { close: true, ...o });
const ellipse = (cx, cy, rx, ry, o = {}, rot = 0) => pen(arcPts(cx, cy, rx, ry, 0, Math.PI * 2, 36, rot).slice(0, -1), { close: true, ...o });
const rect = (x, y, w, h, o = {}) => pen([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], { close: true, ...o });
function withT(x, y, s, rot, fn) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot || 0); ctx.scale(s, s); fn(); ctx.restore(); }

// smooth shapes for the character (no wobble): outlined tube and outlined ellipse
function tube(pts, w, color) {
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const path = () => { ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); };
  path(); ctx.strokeStyle = INK; ctx.lineWidth = w + 11; ctx.stroke();
  path(); ctx.strokeStyle = color; ctx.lineWidth = w; ctx.stroke();
}
function blob(cx, cy, rx, ry, fill, rot = 0, lw = 5.5) {
  ctx.beginPath(); ctx.ellipse(cx, cy, rx, ry, rot, 0, Math.PI * 2);
  ctx.fillStyle = fill; ctx.fill(); ctx.strokeStyle = INK; ctx.lineWidth = lw; ctx.stroke();
}
function poly(pts, fill, lw = 5.5) {
  ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.closePath();
  ctx.fillStyle = fill; ctx.fill(); ctx.strokeStyle = INK; ctx.lineWidth = lw; ctx.lineJoin = 'round'; ctx.stroke();
}

// ------------------------------------------------------------------ props (coloured, ink outlined)
// Same names as the 3D style. Each draws in a box of about ±100 around the origin.
const PROPS = {
  star: p => pen(Array.from({ length: 10 }, (_, i) => { const r = i % 2 ? 40 : 92, a = -Math.PI / 2 + i * Math.PI / 5; return [Math.cos(a) * r, Math.sin(a) * r]; }), { close: true, fill: '#ffd166', p }),
  bulb: p => {
    circle(0, -25, 62, { fill: '#fff3b0', p });
    pen([[-28, 35], [-26, 72], [26, 72], [28, 35]], { fill: '#c9c3b8', p });
    pen([[-22, 84], [22, 84]], { p });
    for (let i = 0; i < 5; i++) { const a = -Math.PI * (0.15 + i * 0.175); pen([[Math.cos(a) * 80, -25 + Math.sin(a) * 80], [Math.cos(a) * 100, -25 + Math.sin(a) * 100]], { p, color: pal[0], w: 6 }); }
  },
  coin: p => { circle(0, 0, 82, { fill: '#ffd166', p }); circle(0, 0, 58, { p, w: 5, fill: '#f6c445' }); pen([[0, -30], [0, 30]], { p, w: 8 }); },
  planet: p => { circle(0, 0, 60, { fill: pal[1], p }); ellipse(0, 0, 108, 26, { p, color: pal[0], w: 8 }, -0.35); },
  globe: p => {
    circle(0, 0, 82, { fill: '#9fd0f2', p }); ellipse(0, 0, 34, 82, { p, w: 5 });
    pen([[-82, 0], [82, 0]], { p, w: 5 }); pen(arcPts(0, -40, 70, 10, 0, Math.PI, 12), { p, w: 4 }); pen(arcPts(0, 40, 70, 10, Math.PI, Math.PI * 2, 12), { p, w: 4 });
    circle(-30, -20, 22, { fill: '#7cc47f', p, w: 4 }); circle(32, 28, 18, { fill: '#7cc47f', p, w: 4 });
  },
  phone: p => { rect(-52, -95, 104, 190, { fill: '#555b66', p }); rect(-40, -78, 80, 140, { fill: '#9fd0f2', p, w: 5 }); circle(0, 78, 8, { p, w: 4, fill: '#dcdcdc' }); },
  bank: p => {
    pen([[-100, -30], [0, -90], [100, -30]], { close: true, fill: pal[0], p });
    for (const x of [-66, -22, 22, 66]) rect(x - 9, -18, 18, 82, { p, w: 5, fill: '#f6efe2' });
    rect(-100, 66, 200, 20, { fill: '#e6dccb', p });
  },
  rocket: p => {
    withT(0, 0, 1, 0.35, () => {
      const f = 18 + Math.sin(T * 30) * 6;
      pen([[-20, 56], [0, 70 + f], [20, 56]], { close: true, fill: '#f39c3d', p, w: 5 });
      pen([[-32, 20], [-58, 62], [-32, 52]], { close: true, fill: pal[0], p });
      pen([[32, 20], [58, 62], [32, 52]], { close: true, fill: pal[0], p });
      pen([[0, -100], [32, -52], [32, 52], [-32, 52], [-32, -52]], { close: true, fill: '#f6efe2', p });
      circle(0, -18, 15, { fill: '#9fd0f2', p, w: 5 });
    });
  },
  brain: p => {
    pen(arcPts(0, 0, 1, 1, 0, Math.PI * 2, 48).slice(0, -1).map(([x, y]) => { const a = Math.atan2(y, x), r = 74 + 9 * Math.sin(a * 9); return [Math.cos(a) * r * 1.15, Math.sin(a) * r * 0.85]; }), { close: true, fill: '#f5a9c4', p });
    pen(Array.from({ length: 9 }, (_, i) => [Math.sin(i * 1.3) * 12, -55 + i * 14]), { p, w: 5 });
  },
  chip: p => {
    for (let i = -2; i <= 2; i++) for (const [x1, y1, x2, y2] of [[i * 22, -64, i * 22, -88], [i * 22, 64, i * 22, 88], [-64, i * 22, -88, i * 22], [64, i * 22, 88, i * 22]]) pen([[x1, y1], [x2, y2]], { p, w: 6, color: '#b9b1a3' });
    rect(-64, -64, 128, 128, { fill: '#555b66', p }); rect(-30, -30, 60, 60, { fill: pal[0], p, w: 5 });
  },
  heart: p => pen(Array.from({ length: 40 }, (_, i) => { const a = (i / 40) * Math.PI * 2; return [80 * Math.pow(Math.sin(a), 3) * 1.05, -(65 * Math.cos(a) - 26 * Math.cos(2 * a) - 10 * Math.cos(3 * a) - 5 * Math.cos(4 * a)) * 1.05 - 8]; }), { close: true, fill: '#e8506b', p }),
  clock: p => {
    circle(0, 0, 84, { fill: '#fffaf0', p }); circle(0, 0, 84, { p, w: 10, color: pal[0] });
    for (let i = 0; i < 12; i++) { const a = (i / 12) * Math.PI * 2; pen([[Math.cos(a) * 62, Math.sin(a) * 62], [Math.cos(a) * 72, Math.sin(a) * 72]], { p, w: 5 }); }
    const a1 = T * 0.5 - Math.PI / 2, a2 = T * 3 - Math.PI / 2;
    pen([[0, 0], [Math.cos(a1) * 38, Math.sin(a1) * 38]], { p, w: 8 }); pen([[0, 0], [Math.cos(a2) * 58, Math.sin(a2) * 58]], { p, w: 5, color: pal[1] });
  },
  gear: p => {
    withT(0, 0, 1, T * 0.8, () => {
      pen(Array.from({ length: 40 }, (_, i) => { const a = (i / 40) * Math.PI * 2, r = i % 4 < 2 ? 88 : 66; return [Math.cos(a) * r, Math.sin(a) * r]; }), { close: true, fill: '#aeb6bf', p, amp: 0.4 });
      circle(0, 0, 26, { fill: pal[2], p });
    });
  },
  atom: p => {
    for (let i = 0; i < 3; i++) ellipse(0, 0, 95, 30, { p, w: 6, color: i === 1 ? pal[0] : INK }, i * Math.PI / 3);
    circle(0, 0, 18, { fill: pal[0], p });
    const a = T * 3; const [ex, ey] = arcPts(0, 0, 95, 30, a, a, 1, Math.PI / 3)[0]; circle(ex, ey, 8, { fill: pal[1], p, w: 4 });
  },
  book: p => {
    pen([[0, -50], [-92, -66], [-92, 56], [0, 72]], { close: true, fill: '#fffaf0', p });
    pen([[0, -50], [92, -66], [92, 56], [0, 72]], { close: true, fill: '#fffaf0', p });
    pen([[-96, 60], [0, 78], [96, 60]], { p, w: 8, color: pal[0] });
    for (let i = 0; i < 3; i++) { pen([[-75, -36 + i * 28], [-18, -26 + i * 28]], { p, w: 4 }); pen([[18, -26 + i * 28], [75, -36 + i * 28]], { p, w: 4 }); }
  },
  magnet: p => {
    pen([[-48, -78], [-48, 10], ...arcPts(0, 10, 48, 52, Math.PI, 0, 16).slice(1, -1), [48, 10], [48, -78]], { p, w: 30, color: '#d9534f', amp: 0.4 });
    pen([[-48, -80], [-48, -52]], { p, w: 30, color: '#c9c3b8', amp: 0.3 }); pen([[48, -80], [48, -52]], { p, w: 30, color: '#c9c3b8', amp: 0.3 });
  },
  cloud: p => { [[0, -10, 52], [-55, 12, 38], [55, 12, 40], [-25, 26, 34], [25, 28, 34]].forEach(([x, y, r]) => circle(x, y, r, { fill: '#ffffff', p })); },
};
const DEFAULT_PROP = { title: 'star', keyword: 'bulb', stat: 'coin' };

// ------------------------------------------------------------------ painted backgrounds (drawn once)
function paintBackground(kind) {
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  let g = c.getContext('2d'); const save = ctx; ctx = g;
  const grad = (y0, y1, a, b) => { const l = g.createLinearGradient(0, y0, 0, y1); l.addColorStop(0, a); l.addColorStop(1, b); return l; };
  // soften far layers without ctx.filter (very slow in software rendering): draw at full size,
  // shrink, then scale back up with smoothing
  const soft = (fn, px = 3) => {
    const big = document.createElement('canvas'); big.width = W; big.height = H;
    const prev = g; ctx = big.getContext('2d'); const real = g; g = ctx; fn(); g = real; ctx = c.getContext('2d');
    const f = 1 / (1 + px), small = document.createElement('canvas'); small.width = Math.round(W * f); small.height = Math.round(H * f);
    const sg = small.getContext('2d'); sg.imageSmoothingQuality = 'high'; sg.drawImage(big, 0, 0, small.width, small.height);
    prev.imageSmoothingEnabled = true; prev.imageSmoothingQuality = 'high'; prev.drawImage(small, 0, 0, W, H);
  };
  const box = (x, y, w, h, fill, line = true) => { g.fillStyle = fill; g.fillRect(x, y, w, h); if (line) { g.strokeStyle = 'rgba(59,42,32,0.55)'; g.lineWidth = 4; g.strokeRect(x, y, w, h); } };
  const floorY = 1150;
  if (kind === 'space') {
    g.fillStyle = grad(0, H, '#1d2147', '#3a3170'); g.fillRect(0, 0, W, H);
    for (let i = 0; i < 160; i++) { g.fillStyle = `rgba(255,248,220,${0.35 + rnd(i + 9) * 0.6})`; g.beginPath(); g.arc(rnd(i) * W, rnd(i + 300) * floorY, 1 + rnd(i + 600) * 2.6, 0, 7); g.fill(); }
    soft(() => { g.fillStyle = '#e9a23b'; g.beginPath(); g.arc(880, 640, 120, 0, 7); g.fill(); g.strokeStyle = '#f4d58d'; g.lineWidth = 14; g.beginPath(); g.ellipse(880, 640, 210, 46, -0.3, 0, 7); g.stroke(); }, 2);
    g.fillStyle = grad(floorY, H, '#9b98a8', '#6e6a80'); g.beginPath(); g.moveTo(0, floorY + 30); g.quadraticCurveTo(540, floorY - 40, W, floorY + 30); g.lineTo(W, H); g.lineTo(0, H); g.fill();
    for (const [x, y, r] of [[150, 1420, 60], [820, 1500, 80], [480, 1700, 50], [960, 1330, 34]]) { g.fillStyle = 'rgba(60,55,80,0.35)'; g.beginPath(); g.ellipse(x, y, r, r * 0.35, 0, 0, 7); g.fill(); }
    return (ctx = save, c);
  }
  if (kind === 'room') {
    g.fillStyle = grad(0, floorY, '#f6e3c3', '#ecd2ab'); g.fillRect(0, 0, W, floorY);
    g.fillStyle = '#e2c49b'; g.fillRect(0, floorY - 210, W, 210);
    g.strokeStyle = 'rgba(59,42,32,0.35)'; g.lineWidth = 4; g.beginPath(); g.moveTo(0, floorY - 210); g.lineTo(W, floorY - 210); g.stroke();
    soft(() => { // window with sky
      box(560, 560, 440, 420, '#bfe1f4');
      g.fillStyle = 'rgba(255,255,255,0.8)'; g.beginPath(); g.ellipse(700, 700, 90, 30, 0, 0, 7); g.ellipse(880, 820, 70, 24, 0, 0, 7); g.fill();
      g.fillStyle = '#a7d39a'; g.beginPath(); g.ellipse(780, 990, 300, 90, 0, Math.PI, 0); g.fill();
      g.strokeStyle = '#8b6a4f'; g.lineWidth = 16; g.strokeRect(560, 560, 440, 420); g.beginPath(); g.moveTo(780, 560); g.lineTo(780, 980); g.moveTo(560, 770); g.lineTo(1000, 770); g.stroke();
      // bookshelf
      box(40, 640, 300, 26, '#8b6a4f'); box(40, 820, 300, 26, '#8b6a4f');
      const cols = ['#d9534f', '#2f80b7', '#e9a23b', '#2f9e8f', '#7b5ea7', '#c0392b', '#3f8fc0'];
      for (let i = 0; i < 9; i++) box(56 + i * 30, 548 + (i % 3) * 12, 24, 92 - (i % 3) * 12, cols[i % cols.length]);
      for (let i = 0; i < 7; i++) box(60 + i * 38, 730 + (i % 2) * 14, 30, 90 - (i % 2) * 14, cols[(i + 3) % cols.length]);
    }, 1.6);
    g.fillStyle = grad(floorY, H, '#c9925f', '#a8744a'); g.fillRect(0, floorY, W, H - floorY);
    g.strokeStyle = 'rgba(70,40,20,0.28)'; g.lineWidth = 3;
    for (let i = -8; i <= 8; i++) { g.beginPath(); g.moveTo(540 + i * 60, floorY); g.lineTo(540 + i * 210, H); g.stroke(); }
    for (const y of [1230, 1340, 1500, 1700]) { g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke(); }
    // plant
    box(950, 1120, 90, 110, '#c76b3c'); for (let i = 0; i < 6; i++) { g.fillStyle = i % 2 ? '#4f9a5a' : '#62b06c'; g.beginPath(); g.ellipse(995 + Math.cos(i) * 40, 1080 - i * 22, 26, 60, -0.5 + i * 0.2, 0, 7); g.fill(); g.strokeStyle = 'rgba(59,42,32,0.5)'; g.lineWidth = 3; g.stroke(); }
    return (ctx = save, c);
  }
  // outdoor scenes share a sky
  g.fillStyle = grad(0, floorY, kind === 'classical' ? '#f3d9b1' : '#9fd3f0', kind === 'classical' ? '#fbefd9' : '#e8f5fb'); g.fillRect(0, 0, W, floorY);
  if (kind === 'nature') {
    soft(() => { g.fillStyle = '#fff2b8'; g.beginPath(); g.arc(860, 300, 80, 0, 7); g.fill(); g.fillStyle = '#b9d9b0'; g.beginPath(); g.ellipse(250, floorY, 520, 260, 0, Math.PI, 0); g.ellipse(860, floorY, 480, 220, 0, Math.PI, 0); g.fill(); }, 4);
    soft(() => { g.fillStyle = '#8fc583'; g.beginPath(); g.ellipse(700, floorY + 30, 700, 160, 0, Math.PI, 0); g.fill(); }, 2);
    for (const [x, s] of [[110, 1.0], [980, 1.2], [880, 0.8]]) { box(x - 14 * s, floorY - 150 * s, 28 * s, 160 * s, '#8b6a4f'); g.fillStyle = '#4f9a5a'; g.beginPath(); g.arc(x, floorY - 190 * s, 80 * s, 0, 7); g.arc(x - 50 * s, floorY - 150 * s, 55 * s, 0, 7); g.arc(x + 50 * s, floorY - 150 * s, 55 * s, 0, 7); g.fill(); }
    g.fillStyle = grad(floorY, H, '#86c06f', '#5f9a4f'); g.fillRect(0, floorY, W, H - floorY);
    return (ctx = save, c);
  }
  if (kind === 'classical') {
    soft(() => { // distant temple
      g.fillStyle = '#ead7b8'; g.fillRect(520, 760, 460, 300); g.fillStyle = '#e2cba6';
      g.beginPath(); g.moveTo(490, 760); g.lineTo(750, 640); g.lineTo(1010, 760); g.fill();
      g.fillStyle = '#f5e8d0'; for (let i = 0; i < 7; i++) g.fillRect(545 + i * 62, 780, 26, 280);
      g.fillStyle = '#a9c79a'; g.beginPath(); g.ellipse(250, floorY, 420, 160, 0, Math.PI, 0); g.fill();
    }, 4);
    for (const x of [-30, 1000]) { // foreground columns at the edges, like a portico
      g.fillStyle = grad(0, 0, '#f1e3c8', '#f1e3c8'); g.fillRect(x, 0, 110, floorY);
      g.fillStyle = 'rgba(160,130,95,0.35)'; for (let k = 0; k < 4; k++) g.fillRect(x + 14 + k * 24, 0, 6, floorY);
      g.strokeStyle = 'rgba(59,42,32,0.5)'; g.lineWidth = 4; g.strokeRect(x, -10, 110, floorY + 10);
      box(x - 20, floorY - 40, 150, 40, '#e6d3b0');
    }
    g.fillStyle = grad(floorY, H, '#e8d6b4', '#cdb38b'); g.fillRect(0, floorY, W, H - floorY);
    g.strokeStyle = 'rgba(90,60,30,0.25)'; g.lineWidth = 3;
    for (let i = -8; i <= 8; i++) { g.beginPath(); g.moveTo(540 + i * 70, floorY); g.lineTo(540 + i * 240, H); g.stroke(); }
    for (const y of [1220, 1320, 1470, 1680]) { g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke(); }
    return (ctx = save, c);
  }
  // town
  soft(() => {
    const cols = ['#f2c6a0', '#c9dfe8', '#f5dfa6', '#d9c3e6', '#bfe0c4', '#f3b9a8'];
    for (let i = 0; i < 7; i++) {
      const x = -40 + i * 165, h = 330 + rnd(i + 3) * 200, y = floorY - h;
      g.fillStyle = cols[i % cols.length]; g.fillRect(x, y, 150, h);
      g.fillStyle = '#b5654a'; g.beginPath(); g.moveTo(x - 10, y); g.lineTo(x + 75, y - 70); g.lineTo(x + 160, y); g.fill();
      g.fillStyle = 'rgba(80,110,140,0.55)'; for (let r = 0; r < 3; r++) for (let q = 0; q < 2; q++) g.fillRect(x + 25 + q * 60, y + 40 + r * 90, 38, 52);
    }
  }, 3);
  g.fillStyle = grad(floorY, H, '#cdbfae', '#a99a88'); g.fillRect(0, floorY, W, H - floorY);
  g.strokeStyle = 'rgba(70,50,30,0.22)'; g.lineWidth = 3;
  for (let r = 0; r < 14; r++) for (let q = 0; q < 12; q++) { g.beginPath(); g.ellipse(q * 100 + (r % 2) * 50, floorY + 30 + r * 55, 44, 20, 0, 0, 7); g.stroke(); }
  return (ctx = save, c);
}
function paintClouds() {
  const c = document.createElement('canvas'); c.width = 520; c.height = 200;
  const g = c.getContext('2d'); g.fillStyle = 'rgba(255,255,255,0.92)';
  g.beginPath(); g.ellipse(150, 120, 120, 50, 0, 0, 7); g.ellipse(250, 90, 100, 60, 0, 0, 7); g.ellipse(360, 120, 110, 45, 0, 0, 7); g.fill();
  return c;
}

// ------------------------------------------------------------------ the presenter character
// Angles: 0 = straight down, positive = towards screen right. [upper, lower] are absolute.
const POSES = {
  stand: { aL: [-0.25, -0.1], aR: [0.25, 0.1], lL: [-0.12, -0.08], lR: [0.12, 0.08], lean: 0, tilt: 0, face: 'smile' },
  point: { aL: [-0.25, -0.1], aR: [1.4, 1.55], lL: [-0.12, -0.08], lR: [0.14, 0.08], lean: 0.04, tilt: 0.05, face: 'grin' },
  wave: { aL: [-0.25, -0.1], aR: [2.4, 2.9], lL: [-0.12, -0.08], lR: [0.12, 0.08], lean: 0, tilt: -0.06, face: 'grin' },
  cheer: { aL: [-2.55, -2.9], aR: [2.55, 2.9], lL: [-0.24, -0.16], lR: [0.24, 0.16], lean: 0, tilt: 0, face: 'grin' },
  shrug: { aL: [-0.95, -2.4], aR: [0.95, 2.4], lL: [-0.12, -0.08], lR: [0.12, 0.08], lean: 0, tilt: 0.14, face: 'flat' },
  think: { aL: [-0.25, -0.1], aR: [0.35, -2.7], lL: [-0.12, -0.08], lR: [0.1, 0.04], lean: -0.03, tilt: -0.12, face: 'hmm' },
  shock: { aL: [-2.0, -2.6], aR: [2.0, 2.6], lL: [-0.22, -0.16], lR: [0.22, 0.16], lean: -0.08, tilt: 0, face: 'shock' },
  walk: { aL: [-0.25, -0.1], aR: [0.25, 0.1], lL: [-0.16, -0.08], lR: [0.16, 0.08], lean: 0.05, tilt: 0, face: 'smile' },
};
const lerpArr = (a, b, k) => a.map((v, i) => lerp(v, b[i], k));
function blendPose(a, b, k) {
  return { aL: lerpArr(a.aL, b.aL, k), aR: lerpArr(a.aR, b.aR, k), lL: lerpArr(a.lL, b.lL, k), lR: lerpArr(a.lR, b.lR, k),
           lean: lerp(a.lean, b.lean, k), tilt: lerp(a.tilt, b.tilt, k), face: k < 0.5 ? a.face : b.face };
}

const FIG_SCALE = 0.84;
function drawPerson(x, ground, pose, lift, talk) {
  ctx.save(); ctx.translate(x, ground); ctx.scale(FIG_SCALE, FIG_SCALE); ctx.translate(-x, -ground);
  const S = 1.0, TH = 84 * S, SH = 80 * S, TORSO = 150 * S, UA = 74 * S, FA = 68 * S, RX = 66 * S, RY = 74 * S;
  const t = T, P = { ...pose, aL: [...pose.aL], aR: [...pose.aR], lL: [...pose.lL], lR: [...pose.lR] };
  const breathe = Math.sin(t * 3) * 0.035;
  P.aL = P.aL.map(v => v - breathe); P.aR = P.aR.map(v => v + breathe);
  if (pose.wave) P.aR[1] += Math.sin(t * 12) * 0.38;
  if (pose.walk) { const w = Math.sin(t * 10); P.lL = [-0.4 * w, -0.4 * w + 0.22]; P.lR = [0.4 * w, 0.4 * w + 0.22]; P.aL = [0.3 * w - 0.15, 0.3 * w]; P.aR = [-0.3 * w + 0.15, -0.3 * w + 0.3]; }
  const dir = a => [Math.sin(a), Math.cos(a)];
  const legEnd = ([a1, a2]) => { const d1 = dir(a1), d2 = dir(a2); return [d1[0] * TH + d2[0] * SH, d1[1] * TH + d2[1] * SH]; };
  const footY = Math.max(legEnd(P.lL)[1], legEnd(P.lR)[1]);
  const hip = [x, ground - footY - 14 - lift - Math.abs(Math.sin(t * 3)) * 2];
  const up = [Math.sin(P.lean), -Math.cos(P.lean)], side = [-up[1], up[0]];
  const at = (o, a, b) => [o[0] + up[0] * a + side[0] * b, o[1] + up[1] * a + side[1] * b];
  const neck = at(hip, TORSO, 0), sh = at(hip, TORSO - 18, 0);
  const limbPts = (o, [a1, a2], l1, l2) => { const d1 = dir(a1), d2 = dir(a2), m = [o[0] + d1[0] * l1, o[1] + d1[1] * l1]; return [o, m, [m[0] + d2[0] * l2, m[1] + d2[1] * l2]]; };
  const shoe = (p) => blob(p[0] + 14, p[1] + 6, 32, 16, SHOE);
  const hand = (p) => blob(p[0], p[1], 16, 16, SKIN, 0, 5);

  // shadow on the floor
  ctx.save(); ctx.fillStyle = 'rgba(40,25,15,0.18)'; ctx.beginPath(); ctx.ellipse(x + 6, ground + 6, 95 * (1 - lift / 500), 18, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  // back arm and back leg
  const armL = limbPts(at(sh, 0, -30), P.aL, UA, FA);
  tube(armL, 30, SHIRT_SH); hand(armL[2]);
  const legL = limbPts(at(hip, 0, -18), P.lL, TH, SH); tube(legL, 36, PANTS); shoe(legL[2]);
  const legR = limbPts(at(hip, 0, 18), P.lR, TH, SH); tube(legR, 36, PANTS); shoe(legR[2]);
  // torso (shirt) with cel shade, collar and belt
  const torso = [at(neck, -10, -48), at(neck, -10, 48), at(hip, 0, 42), at(hip, 0, -42)];
  poly(torso, SHIRT);
  ctx.save(); ctx.beginPath(); torso.forEach(([px, py], i) => (i ? ctx.lineTo(px, py) : ctx.moveTo(px, py))); ctx.closePath(); ctx.clip();
  ctx.fillStyle = SHIRT_SH; const sA = at(neck, 0, 18), sB = at(hip, 0, 14);
  ctx.beginPath(); ctx.moveTo(sA[0], sA[1]); ctx.lineTo(sA[0] + 80, sA[1]); ctx.lineTo(sB[0] + 80, sB[1]); ctx.lineTo(sB[0], sB[1]); ctx.fill(); ctx.restore();
  poly(torso, 'rgba(0,0,0,0)');
  tube([at(hip, 6, -40), at(hip, 6, 40)], 8, '#4a3426');
  // neck and collar
  tube([at(neck, -8, 0), at(neck, 18, 0)], 26, SKIN);
  poly([at(neck, -4, -30), at(neck, -40, 0), at(neck, -4, 30), at(neck, -16, 0)], COLLAR, 4.5);
  // head: back hair, head, ear, top hair, face
  const hc = at(neck, 18 + RY - 6, 6);
  const tilt = P.tilt;
  ctx.save(); ctx.translate(hc[0], hc[1]); ctx.rotate(tilt + P.lean);
  for (let i = 0; i < 9; i++) { const a = Math.PI * (0.62 + i * 0.13); blob(Math.cos(a) * RX * 0.92 - 8, Math.sin(a) * RY * 0.92, 30, 30, HAIR, 0, 5); }
  blob(0, 0, RX, RY, SKIN);
  ctx.save(); ctx.beginPath(); ctx.ellipse(0, 0, RX, RY, 0, 0, Math.PI * 2); ctx.clip();
  ctx.fillStyle = SKIN_SH; ctx.beginPath(); ctx.ellipse(-RX * 0.85, 10, RX * 0.5, RY, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  blob(0, 0, RX, RY, 'rgba(0,0,0,0)');
  blob(-RX * 0.42, 8, 15, 20, SKIN, 0, 5);
  for (let i = 0; i < 7; i++) { const a = Math.PI * (1.08 + i * 0.12); blob(Math.cos(a) * RX * 0.8, Math.sin(a) * RY * 0.82 + 6, 28, 26, HAIR, 0, 5); }
  // face looks to screen right (towards the bubble)
  const fx = RX * 0.32, ey = -6, blink = (t % 3.4) < 0.11, face = P.face;
  ctx.fillStyle = 'rgba(232,110,110,0.28)'; ctx.beginPath(); ctx.ellipse(fx + 6, 30, 16, 10, 0, 0, Math.PI * 2); ctx.fill();
  for (const ex of [fx - 14, fx + 24]) {
    const big = face === 'shock' ? 1.25 : 1;
    if (blink) { ctx.strokeStyle = INK; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(ex - 11, ey); ctx.quadraticCurveTo(ex, ey + 6, ex + 11, ey); ctx.stroke(); }
    else {
      blob(ex, ey, 12 * big, 17 * big, '#ffffff', 0, 4.5);
      ctx.fillStyle = INK; ctx.beginPath(); ctx.ellipse(ex + 4 + (face === 'hmm' ? -3 : 0), ey + (face === 'hmm' ? -6 : 2), 5.5, 7.5, 0, 0, Math.PI * 2); ctx.fill();
    }
    const by = ey - 30 - (face === 'shock' ? 12 : 0) + (face === 'flat' ? 6 : 0) - (face === 'hmm' && ex > fx ? 8 : 0);
    ctx.strokeStyle = HAIR; ctx.lineWidth = 7; ctx.lineCap = 'round'; ctx.beginPath();
    ctx.moveTo(ex - 12, by + (face === 'flat' ? 0 : 4)); ctx.quadraticCurveTo(ex, by - (face === 'flat' ? 0 : 6), ex + 12, by + (face === 'hmm' && ex < fx ? 6 : 2)); ctx.stroke();
  }
  // big friendly nose pointing right
  blob(fx + 46, 14, 22, 17, SKIN, -0.2, 5);
  // mouth: talks while narrating, otherwise shows the expression
  const mx = fx + 8, my = 42;
  if (face === 'shock') blob(mx, my + 4, 11, 15, '#7a2e2e', 0, 5);
  else if (talk > 0.08) { blob(mx, my, 18, 3 + 13 * talk, '#7a2e2e', 0, 5); if (talk > 0.4) { ctx.fillStyle = '#e57a7a'; ctx.beginPath(); ctx.ellipse(mx, my + 7 * talk, 9, 4 * talk, 0, 0, Math.PI * 2); ctx.fill(); } }
  else if (face === 'grin') { ctx.beginPath(); ctx.moveTo(mx - 20, my - 4); ctx.quadraticCurveTo(mx, my + 22, mx + 22, my - 6); ctx.closePath(); ctx.fillStyle = '#fff'; ctx.fill(); ctx.strokeStyle = INK; ctx.lineWidth = 5; ctx.stroke(); }
  else { ctx.strokeStyle = INK; ctx.lineWidth = 5; ctx.lineCap = 'round'; ctx.beginPath();
    if (face === 'flat') { ctx.moveTo(mx - 14, my); ctx.lineTo(mx + 14, my + 2); }
    else if (face === 'hmm') { ctx.moveTo(mx - 14, my + 2); ctx.quadraticCurveTo(mx, my - 2, mx + 14, my - 6); }
    else { ctx.moveTo(mx - 16, my - 4); ctx.quadraticCurveTo(mx, my + 12, mx + 18, my - 6); }
    ctx.stroke(); }
  ctx.restore();
  if (face === 'shock') for (const k of [-1, 1]) pen([[hc[0] + k * 92, hc[1] - 70], [hc[0] + k * 116, hc[1] - 96]], { w: 7, color: pal[0] });
  if (face === 'hmm') { ctx.save(); ctx.fillStyle = (segs.length && segsKind[segs.findIndex(x => T >= x.start && T < x.end)] === 'space') ? '#fff8e8' : INK; ctx.font = '900 64px sans-serif'; ctx.fillText('?', hc[0] + 84, hc[1] - 70 + 5 * Math.sin(t * 4)); ctx.restore(); }
  // front arm on top
  const armR = limbPts(at(sh, 0, 30), P.aR, UA, FA);
  tube(armR, 30, SHIRT); hand(armR[2]);
  ctx.restore();
  return { head: [x + (hc[0] - x) * FIG_SCALE, ground + (hc[1] - ground) * FIG_SCALE] };
}

// ------------------------------------------------------------------ stat parsing (mirrors shorts/motion.py)
function parseNumber(s) {
  const m = s.trim().match(/^(\D*?)(-?\d[\d,]*(?:\.\d+)?)(.*)$/);
  if (!m) return null;
  const raw = m[2], decimals = raw.includes('.') ? raw.split('.')[1].length : 0;
  const value = parseFloat(raw.replace(/,/g, ''));
  const isYear = !m[1].trim() && !m[3].trim() && decimals === 0 && value >= 1000 && value <= 2100;
  return { prefix: m[1], value, suffix: m[3].trim(), decimals, commas: raw.includes(','), isYear };
}
const fmt = (v, d, commas) => commas ? v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }) : v.toFixed(d);

// ------------------------------------------------------------------ segments
function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
const HOME = { title: 270, keyword: 260, stat: 250, steps: 170, compare: 220, flow: 225, race: 225, build: 225, cycle: 225 };
const DIAGRAM_OK = { flow: g => g.items?.length >= 2, build: g => g.items?.length >= 2, cycle: g => g.items?.length >= 3,
                     race: g => g.items?.length === 2 && g.values?.length === 2 && Math.min(...g.values) > 0 };

function buildSegment(seg, i, all) {
  const g = seg.graphic, kind = g.kind;
  const card = el('div', 'card'); card.style.display = 'none';
  const s = { ...seg, g, kind, card, i, last: i === all.length - 1, home: HOME[kind] ?? 270 };
  const headline = (txt, size) => {
    const h = el('div', 'head'); if (size) h.style.fontSize = size;
    const mk = el('span', 'mk'); s.words = [];
    txt.split(' ').forEach((w, j) => { const sp = el('span', 'w', w); mk.append(sp); if (j < txt.split(' ').length - 1) mk.append(document.createTextNode(' ')); s.words.push(sp); });
    h.append(mk); s.mark = mk; card.append(h); return h;
  };
  if (kind === 'stat' && parseNumber(g.headline)) {
    s.num = parseNumber(g.headline);
    s.big = el('div', 'big'); s.big.style.color = pal[0]; card.append(s.big);
    if (s.num.suffix) card.append(el('div', 'unit', s.num.suffix));
    if (g.caption) card.append(el('div', 'cap', g.caption));
  } else if (kind === 'steps' && g.items?.length >= 2) {
    headline(g.headline, '58px');
    const list = el('div', 'steps');
    s.items = g.items.slice(0, 4).map((txt, k) => { const d = el('div', 'step'); d.append(el('b', null, String(k + 1)), document.createTextNode(txt)); list.append(d); return d; });
    card.append(list);
    const n = s.items.length;
    s.pads = s.items.map((_, k) => 380 + (k * 480) / Math.max(1, n - 1));
  } else if (kind === 'compare' && g.items?.length === 2) {
    headline(g.headline, '66px');
    const row = el('div', 'cmp');
    g.items.forEach((txt, k) => { const d = el('div', null, txt); d.style.background = k ? pal[1] : pal[0]; row.append(d); });
    card.append(row);
    const vals = g.values?.length === 2 && Math.max(...g.values) > 0 ? g.values : [1, 1];
    s.bars = vals.map(v => v / Math.max(...vals));
  } else if (DIAGRAM_OK[kind] && DIAGRAM_OK[kind](g)) {
    headline(g.headline, '70px');
    if (g.caption) card.append(el('div', 'cap', g.caption));
    s.diagram = kind; s.labels = g.items.slice(0, 4); s.vals = g.values || [];
  } else {
    const h = headline(g.headline, kind === 'title' ? '88px' : '80px');
    if (kind === 'keyword') h.style.color = pal[0];
    if (g.caption) card.append(el('div', 'cap', g.caption));
    s.prop = PROPS[g.prop] ? g.prop : (DEFAULT_PROP[kind] || 'star');
  }
  const hold = Math.max(0.6, s.end - s.start - INTRO - OUTRO), mid = s.start + INTRO + hold * 0.45;
  const k = [];
  if (kind === 'title' && i === 0) k.push([s.start, 'shock'], [s.start + 1.3, 'point']);
  else if (s.last) k.push([s.start, 'wave'], [s.start + INTRO + hold * 0.6, 'cheer']);
  else if (kind === 'title') k.push([s.start, 'point']);
  else if (kind === 'keyword') k.push([s.start, 'think'], [s.hit ? Math.max(s.start + 0.4, s.hit - 0.25) : mid, 'point']);
  else if (kind === 'stat') k.push([s.start, 'stand'], [s.hit ? Math.max(s.start + 0.4, s.hit - 0.15) : s.start + 1.6, 'shock']);
  else if (s.diagram === 'race') k.push([s.start, 'point'], [s.hit ? Math.max(s.start + 0.4, s.hit - 0.15) : s.start + INTRO + hold * 0.6, 'shock']);
  else if (s.diagram) k.push([s.start, 'point']);
  else if (kind === 'steps') k.push([s.start, 'point']);
  else if (kind === 'compare') k.push([s.start, 'point'], [s.start + INTRO + hold * 0.7, 'shrug']);
  else k.push([s.start, 'stand']);
  if (g.pose && POSES[g.pose]) k.splice(1, k.length, [s.start + Math.min(1.0, hold * 0.3), g.pose]);
  s.keys = k;
  s.focus = s.prop ? [770, 960] : s.diagram ? [737, 990] : s.num ? [700, 1050] : null;
  s.pushAt = s.hit ? s.hit - 0.15 : s.start + (s.end - s.start) * 0.45;
  if (i === 0) card.style.top = '470px'; // keep clear of the hook text shown in the first seconds
  document.getElementById('cards').append(card);
  return s;
}

function poseAt(s, t) {
  let cur = POSES[s.keys[0][1]], prev = cur, since = 1e9;
  for (const [kt, name] of s.keys) if (t >= kt) { prev = cur; cur = { ...POSES[name], [name]: true }; since = t - kt; }
  const k = easeInOut(clamp(since / 0.28));
  return { ...blendPose(prev, cur, k), wave: cur.wave, walk: cur.walk };
}

function figureAt(s, t) {
  const prevHome = s.i > 0 ? segs[s.i - 1].home : s.home;
  if (s.pads) {
    const holdStart = s.start + INTRO, holdEnd = s.end - OUTRO, n = s.pads.length;
    const per = Math.max(0.3, (holdEnd - holdStart) / n), HOP = 0.45;
    const stops = [{ t: -1e9, x: s.home }];
    s.pads.forEach((px, k) => stops.push({ t: holdStart + k * per, x: px }));
    for (let k = stops.length - 1; k >= 1; k--) {
      const a = stops[k - 1], b = stops[k];
      if (t >= b.t) return { x: b.x, lift: 0, walk: false, onPad: k - 1 };
      if (t >= b.t - HOP) { const p = clamp((t - (b.t - HOP)) / HOP); return { x: lerp(a.x, b.x, easeInOut(p)), lift: Math.sin(Math.PI * p) * 80, walk: false, onPad: k - 2 }; }
    }
  }
  const p = clamp((t - s.start) / 0.55);
  return { x: lerp(prevHome, s.home, easeInOut(p)), lift: 0, walk: p < 1 && Math.abs(prevHome - s.home) > 20, onPad: -1 };
}

// round inset ("thought bubble") holding the scene's subject
function bubble(cx, cy, r, k, from, propName, u, exit) {
  if (k <= 0.001) return;
  if (from) for (let j = 0; j < 3; j++) { // trailing dots from the presenter's head
    const f = 0.25 + j * 0.22, bx = lerp(from[0] + 70, cx - r * 0.75, f), by = lerp(from[1] - 60, cy + r * 0.45, f);
    const rr = (9 + j * 7) * clamp(k * 1.4 - j * 0.15);
    if (rr > 0.5) blob(bx, by, rr, rr, '#fffaf0', 0, 4.5);
  }
  ctx.save(); ctx.translate(cx, cy); ctx.scale(k, k);
  const g = ctx.createRadialGradient(-r * 0.3, -r * 0.35, r * 0.1, 0, 0, r);
  g.addColorStop(0, '#ffffff'); g.addColorStop(1, pal[2]);
  ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fillStyle = g; ctx.fill();
  ctx.save(); ctx.clip();
  ctx.fillStyle = 'rgba(59,42,32,0.07)'; ctx.beginPath(); ctx.ellipse(0, r * 0.62, r * 0.75, r * 0.18, 0, 0, Math.PI * 2); ctx.fill();
  withT(0, Math.sin(T * 2.2) * 8, 1.25, Math.sin(T * 1.3) * 0.05, () => PROPS[propName](clamp((u - 0.25) / 0.8) * exit));
  ctx.restore();
  ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.strokeStyle = INK; ctx.lineWidth = 8; ctx.stroke();
  ctx.restore();
}

function updateSegment(s, t) {
  const u = t - s.start;
  const enter = clamp(u / INTRO), exit = clamp((s.end - t) / OUTRO), k = easeOutBack(enter) * easeInOut(exit);
  const holdStart = s.start + INTRO, holdEnd = s.end - OUTRO;
  s.card.style.display = 'block';
  s.card.style.opacity = String(clamp(enter * 2) * exit);
  // kazi: the main motion lands ~3 frames before the keyword; give it a visible extra kick
  const pk = s.hit ? clamp(1 - Math.abs(t - (s.hit - 0.03)) / 0.2) : 0;
  s.card.style.transform = `translateY(${(1 - enter) * 40}px) scale(${(0.85 + 0.15 * k) * (1 + 0.05 * pk)})`;
  if (s.words) s.words.forEach((w, j) => {
    const a = clamp((u - 0.12 - j * 0.1) / 0.1);
    w.style.opacity = String(a); w.style.display = 'inline-block';
    w.style.transform = `translateY(${(1 - a) * 18}px)`;
  });
  if (s.mark && (s.kind === 'keyword' || s.kind === 'title' || s.diagram)) {
    const m0 = s.hit ? Math.max(s.start + 0.3, s.hit - 0.35) : s.start + 0.7;
    const mp = expoOut(clamp((t - m0) / 0.35));
    s.mark.style.backgroundSize = `${mp * 100}% 44%`;
  }
  const fig = figureAt(s, t);
  if (s.diagram) drawDiagram(s, t, u, exit, pk);

  if (s.num) {
    const c0 = s.hit ? Math.max(s.start, s.hit - 1.5) : s.start, cu = t - c0;
    const p = s.num.isYear ? 1 : easeOutCubic(clamp(cu / 1.4));
    s.big.textContent = s.num.prefix + fmt(s.num.value * p, s.num.decimals, s.num.commas);
    s.big.style.transform = `scale(${stampAt(t - (c0 + 1.4))})`;
    const coins = Math.ceil(clamp(easeOutCubic(clamp(cu / 1.4))) * 8);
    for (let c = 0; c < coins; c++) { ellipse(780 + Math.sin(c * 2.1) * 8, GROUND - 22 - c * 34, 92, 24, { fill: c % 2 ? '#f6c445' : '#ffd166', w: 6, p: exit }); }
    if (u > 1.5) for (let j = 0; j < 4; j++) { const a = -Math.PI / 2 + (j - 1.5) * 0.5; pen([[780 + Math.cos(a) * 130, GROUND - 330 + Math.sin(a) * 60], [780 + Math.cos(a) * 165, GROUND - 330 + Math.sin(a) * 90]], { w: 7, color: pal[0], p: clamp((u - 1.5) / 0.3) * exit }); }
  }
  if (s.items) {
    const n = s.items.length, per = Math.max(0.3, (holdEnd - holdStart) / n);
    const active = clamp(Math.floor((t - holdStart) / per), -1, n - 1);
    s.items.forEach((d, j) => { d.className = j === active ? 'step on' : j < active ? 'step done' : 'step'; d.style.background = j === active ? pal[2] : 'transparent'; d.firstChild.style.background = j <= active ? pal[0] : '#b9a796'; });
    s.pads.forEach((px, j) => {
      const on = j === active, kk = clamp((u - j * 0.12) / 0.5) * exit;
      if (kk <= 0) return;
      blob(px, GROUND + 2, 80 * kk, 22 * kk, '#8e7a66', 0, 5); blob(px, GROUND - 6, 80 * kk, 22 * kk, on ? pal[0] : '#efe3cf', 0, 5);
      ctx.save(); ctx.globalAlpha = exit; ctx.fillStyle = on ? '#ffffff' : INK; ctx.font = '900 30px sans-serif'; ctx.textAlign = 'center'; ctx.fillText(String(j + 1), px, GROUND + 4); ctx.restore();
    });
  }
  if (s.bars) s.bars.forEach((v, j) => { // two classical columns rising, like a bar chart
    const grow = easeOutBack(clamp((u - 0.25 - j * 0.3) / 0.8)) * exit, x = 620 + j * 230, h = Math.max(6, 330 * v * grow);
    if (grow <= 0.01) return;
    const col = j ? pal[1] : pal[0];
    poly([[x - 14, GROUND], [x + 154, GROUND], [x + 146, GROUND - 22], [x - 6, GROUND - 22]], '#efe3cf');
    poly([[x, GROUND - 22], [x + 140, GROUND - 22], [x + 140, GROUND - 22 - h], [x, GROUND - 22 - h]], col);
    ctx.save(); ctx.fillStyle = 'rgba(255,255,255,0.28)'; for (let q = 0; q < 3; q++) ctx.fillRect(x + 18 + q * 40, GROUND - 18 - h, 12, h - 8); ctx.restore();
    poly([[x - 16, GROUND - 22 - h], [x + 156, GROUND - 22 - h], [x + 148, GROUND - 48 - h], [x - 8, GROUND - 48 - h]], '#efe3cf');
  });

  const pose = poseAt(s, t);
  if (fig.walk) { pose.walk = true; pose.face = 'smile'; }
  // talking: the narration plays during the hold; flap the mouth with two mixed rhythms
  const speaking = t > s.start + 0.15 && t < s.end - 0.25 && !fig.walk;
  const talk = speaking ? clamp(0.5 + 0.5 * Math.sin(t * 15)) * clamp(0.55 + 0.45 * Math.sin(t * 4.7 + s.i)) : 0;
  const person = drawPerson(fig.x, s.pads && fig.onPad >= 0 ? GROUND - 16 : GROUND, pose, fig.lift, talk);
  if (s.prop) {
    const b0 = s.hit ? Math.max(s.start + 0.05, s.hit - 0.6) : s.start + 0.1;
    const bk = popAt(t - b0) * easeInOut(exit) * (1 + 0.07 * pk);
    bubble(770, 960, 180, bk, s.kind === 'keyword' || (s.kind === 'title' && s.i === 0) ? person.head : null, s.prop, u, exit);
    if (s.kind === 'title') for (let j = 0; j < 5; j++) { const a = -2.6 + j * 0.42; pen([[770 + Math.cos(a) * 200, 960 + Math.sin(a) * 200], [770 + Math.cos(a) * 236, 960 + Math.sin(a) * 236]], { w: 7, color: pal[0], p: clamp((u - 0.6 - j * 0.08) / 0.3) * exit }); }
  }
}


// ------------------------------------------------------------------ animated diagrams on an easel board
// Visual grammars from the canvas-explainer-videos skill (pipeline, A/B comparison, progressive
// build, state loop) with progressive disclosure from iart's diagram-animation skill:
// nodes, then edges, then labels; the active element is highlighted, the rest dimmed.
const BOARD = { x: 430, y: 755, w: 615, h: 470 };
function fitText(str, x, y, maxW, size, color, align = 'left', weight = 800) {
  let f = size;
  ctx.font = `${weight} ${f}px "Noto Sans", "Noto Sans Devanagari", sans-serif`;
  while (f > 18 && ctx.measureText(str).width > maxW) { f -= 2; ctx.font = `${weight} ${f}px "Noto Sans", "Noto Sans Devanagari", sans-serif`; }
  ctx.fillStyle = color; ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.fillText(str, x, y);
}
function drawBoard(k) {
  const { x, y, w, h } = BOARD;
  ctx.save(); ctx.translate(x + w / 2, y + h); ctx.scale(1, k); ctx.translate(-(x + w / 2), -(y + h));
  tube([[x + 90, y + h - 10], [x + 60, GROUND + 4]], 12, '#8b6a4f'); tube([[x + w - 90, y + h - 10], [x + w - 60, GROUND + 4]], 12, '#8b6a4f');
  ctx.fillStyle = 'rgba(40,25,15,0.18)'; ctx.fillRect(x + 10, y + 14, w, h);
  poly([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], '#8b6a4f', 6);
  poly([[x + 16, y + 16], [x + w - 16, y + 16], [x + w - 16, y + h - 16], [x + 16, y + h - 16]], '#fffaf0', 4);
  ctx.strokeStyle = 'rgba(59,42,32,0.06)'; ctx.lineWidth = 2;
  for (let gx = x + 56; gx < x + w - 16; gx += 40) { ctx.beginPath(); ctx.moveTo(gx, y + 16); ctx.lineTo(gx, y + h - 16); ctx.stroke(); }
  for (let gy = y + 56; gy < y + h - 16; gy += 40) { ctx.beginPath(); ctx.moveTo(x + 16, gy); ctx.lineTo(x + w - 16, gy); ctx.stroke(); }
  ctx.restore();
}
function dot(x, y, r, fill, glow = 0) {
  ctx.save(); if (glow) { ctx.shadowColor = fill; ctx.shadowBlur = glow; }
  ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fillStyle = fill; ctx.fill(); ctx.restore();
}
function drawDiagram(s, t, u, exit, pk) {
  const bk = Math.min(1.12, popAt(u - 0.05)) * easeInOut(exit);
  if (bk <= 0.01) return;
  drawBoard(bk);
  if (bk < 0.6) return;
  const { x: BX, y: BY, w: BW, h: BH } = BOARD;
  const t0 = s.start + INTRO * 0.8, D = Math.max(0.8, s.end - OUTRO - t0);
  const L = s.labels, n = L.length;
  ctx.save(); ctx.globalAlpha = clamp(exit * 1.5);
  if (s.diagram === 'flow') { // pipeline: things move along the chain
    const ys = L.map((_, j) => BY + 78 + j * ((BH - 156) / Math.max(1, n - 1)));
    const cx = BX + 100;
    L.forEach((lab, j) => {
      const on = t >= t0 + (j * D) / (n + 0.6);
      const a = clamp((t - (t0 + (j * D) / (n + 0.6))) / 0.35);
      if (j < n - 1) { // edge draws on after the next node appears, then carries particles
        const e0 = t0 + ((j + 1) * D) / (n + 0.6);
        const ep = clamp((t - e0 + 0.25) / 0.45);
        if (ep > 0) {
          pen([[cx, ys[j] + 40], [cx, ys[j] + 40 + (ys[j + 1] - ys[j] - 80) * ep]], { w: 7, color: '#b9a796', amp: 0 });
          if (ep >= 1) for (let q = 0; q < 4; q++) {
            const f = ((t * 0.9 + q / 4) % 1), py = ys[j] + 40 + (ys[j + 1] - ys[j] - 80) * f;
            dot(cx, py, 12, pal[0], 12);
          }
        }
      }
      if (a <= 0) return;
      const last = t >= t0 + ((j + 1) * D) / (n + 0.6);
      const active = on && (!last || j === n - 1);
      const r = 38 * easeOutBack(a) * (active ? 1 + 0.08 * pk : 1);
      blob(cx, ys[j], r, r, active ? pal[0] : '#efe3cf', 0, 5);
      fitText(String(j + 1), cx, ys[j] + 2, 60, 34, active ? '#ffffff' : INK, 'center', 900);
      ctx.save(); ctx.globalAlpha *= clamp((t - (t0 + (j * D) / (n + 0.6)) - 0.15) / 0.3);
      fitText(lab, cx + 62, ys[j], BW - 190, 40, active ? INK : '#8a7666', 'left', active ? 900 : 700);
      ctx.restore();
    });
  } else if (s.diagram === 'race') { // A/B comparison with a countable difference
    const vmax = Math.max(...s.vals), x0 = BX + 50, x1 = BX + BW - 120, len = x1 - x0, gap = 0.32;
    L.forEach((lab, j) => {
      const y = BY + 140 + j * 200, col = j ? pal[1] : pal[0];
      const speed = Math.max(4, 420 * s.vals[j] / vmax), ts = t0 + 0.3;
      fitText(lab, x0, y - 62, BW - 120, 40, INK, 'left', 900);
      pen([[x0, y], [x1, y]], { w: 6, color: '#cdbfae', amp: 0 });
      pen([[x1 + 6, y - 34], [x1 + 6, y + 34]], { w: 7, color: INK, amp: 0 });
      const m = Math.floor((t - ts) / gap);
      for (let q = Math.max(0, m - 40); q <= m; q++) {
        const px = x0 + speed * (t - (ts + q * gap));
        if (px >= x0 && px <= x1) dot(px, y, 15, col, 10);
      }
      const arrived = t < ts ? 0 : Math.max(0, Math.floor((t - ts - len / speed) / gap) + 1);
      blob(x1 + 62, y, 46 * (1 + 0.1 * pk), 40 * (1 + 0.1 * pk), col, 0, 5);
      fitText(String(arrived), x1 + 62, y + 2, 80, 38, '#ffffff', 'center', 900);
    });
  } else if (s.diagram === 'build') { // progressive build: one layer at a time
    L.forEach((lab, j) => {
      const at = t0 + (j * D) / (n + 0.4), a = clamp((t - at) / 0.45);
      if (a <= 0) return;
      const top = t >= at && (j === n - 1 || t < t0 + ((j + 1) * D) / (n + 0.4));
      const hgt = Math.min(92, (BH - 90) / n - 12), y = BY + BH - 40 - (j + 1) * (hgt + 12) - (1 - easeOutBack(a)) * 160;
      const w = BW - 150 - j * 20, x = BX + (BW - w) / 2;
      ctx.save(); ctx.globalAlpha *= clamp(a * 2);
      poly([[x, y], [x + w, y], [x + w, y + hgt], [x, y + hgt]], top ? pal[0] : (j % 2 ? '#e8d9c2' : '#f3e7d3'), 5);
      fitText(lab, x + w / 2, y + hgt / 2 + 2, w - 30, 38, top ? '#ffffff' : INK, 'center', 900);
      ctx.restore();
    });
  } else if (s.diagram === 'cycle') { // state loop with a travelling token
    const cx = BX + BW / 2, cy = BY + BH / 2, R = 160, ring = clamp((t - t0) / 0.8);
    const ang = j => -Math.PI / 2 + (j * Math.PI * 2) / n;
    pen(arcPts(cx, cy, R, R, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * ring, 60), { w: 7, color: '#cdbfae', amp: 0 });
    const lap = Math.max(2.4, D / 1.5), ta = ang(0) + (Math.max(0, t - t0 - 0.6) / lap) * Math.PI * 2;
    const activeIdx = Math.floor((((ta + Math.PI / 2) / (Math.PI * 2)) % 1) * n + 1e-6) % n;
    if (t > t0 + 0.6) dot(cx + Math.cos(ta) * R, cy + Math.sin(ta) * R, 20, pal[0], 16);
    L.forEach((lab, j) => {
      const a = clamp((t - t0 - j * 0.25) / 0.4);
      if (a <= 0) return;
      const px = cx + Math.cos(ang(j)) * R, py = cy + Math.sin(ang(j)) * R, on = t > t0 + 0.6 && j === activeIdx;
      const w = 220 * easeOutBack(a) * (on ? 1 + 0.06 * pk : 1), h = 66 * easeOutBack(a);
      poly([[px - w / 2, py - h / 2], [px + w / 2, py - h / 2], [px + w / 2, py + h / 2], [px - w / 2, py + h / 2]], on ? pal[0] : '#efe3cf', 5);
      fitText(lab, px, py + 2, w - 24, 34, on ? '#ffffff' : INK, 'center', 900);
    });
  }
  ctx.restore();
}

// ------------------------------------------------------------------ public API
window.setup = async (config) => {
  cfg = config;
  pal = PALETTES[hash(cfg.niche || 'x') % PALETTES.length];
  document.getElementById('pill').textContent = cfg.lang === 'en' ? (cfg.niche || '').toUpperCase() : (cfg.niche || '');
  document.getElementById('fill').style.background = pal[0];
  document.body.lang = cfg.lang === 'hi' ? 'hi' : 'en';
  ctx = document.getElementById('cv').getContext('2d');
  kindOfBg = cfg.backdrop || BACKDROP[cfg.niche] || 'room';
  // a different backdrop for every scene: the scene's stock photo if there is one, otherwise
  // the painted sets in rotation, starting with the niche's own
  const order = [kindOfBg, ...['room', 'town', 'nature', 'classical', 'space'].filter(k => k !== kindOfBg)];
  const painted = {};
  const paint = k => (painted[k] = painted[k] || paintBackground(k));
  bg = paint(kindOfBg); clouds = paintClouds(); makeGrain();
  let n = 0;
  await Promise.all(cfg.segments.map(async (sg, i) => {
    if (!sg.photo) return;
    const img = new Image(); img.src = sg.photo;
    try { await img.decode(); segsPhoto[i] = img; } catch (e) { /* fall back to painted */ }
  }));
  cfg.segments.forEach((sg, i) => { segsKind[i] = segsPhoto[i] ? kindOfBg : order[(n++) % order.length]; segsBg[i] = paint(segsKind[i]); });
  segs = cfg.segments.map((s, i, all) => buildSegment(s, i, all));
  await document.fonts.ready;
};

// Camera that never freezes: whip-pan in after each cut, slow drift, a cut-in push to the
// scene's focus on the keyword beat, and a whip-pan out before the next cut.
function cameraAt(s, t) {
  const u = t - s.start, left = s.end - t;
  let dx = 0;
  const inStep = Math.floor(u * 12);
  if (s.i > 0 && inStep < 10) dx += 0.392 * W * Math.pow(0.6, inStep + 1);
  const outStep = Math.floor(left * 12);
  if (!s.last && outStep < WHIP_OUT.length) dx += WHIP_OUT[outStep] * W;
  const drift = 0.03 * clamp(u / Math.max(1, s.end - s.start));
  const push = s.focus ? expoOut(clamp((t - s.pushAt) / 0.5)) * clamp(left / 0.25) : 0;
  const z = 1 + drift + 0.16 * push;
  const fx = s.focus ? lerp(W / 2, s.focus[0], push) : W / 2, fy = s.focus ? lerp(1050, s.focus[1], push) : 1050;
  return { dx, z, fx, fy };
}
let GRAIN = [], VIGNETTE;
function makeGrain() {
  for (let k = 0; k < 4; k++) {
    const c = document.createElement('canvas'); c.width = 270; c.height = 480;
    const g = c.getContext('2d'), img = g.createImageData(270, 480);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = rnd(i * 0.37 + k * 9991), on = v > 0.5;
      img.data[i] = img.data[i + 1] = img.data[i + 2] = on ? 255 : 40;
      img.data[i + 3] = Math.floor(Math.abs(v - 0.5) * 2 * 22);
    }
    g.putImageData(img, 0, 0); GRAIN.push(c);
  }
  VIGNETTE = document.createElement('canvas'); VIGNETTE.width = W; VIGNETTE.height = H;
  const vg = VIGNETTE.getContext('2d'), gr = vg.createRadialGradient(W / 2, H * 0.52, H * 0.3, W / 2, H * 0.52, H * 0.78);
  gr.addColorStop(0, 'rgba(40,20,10,0)'); gr.addColorStop(1, 'rgba(40,20,10,0.32)');
  vg.fillStyle = gr; vg.fillRect(0, 0, W, H);
}

const FLOOR_Y = 1150;
function drawBackdrop(s, t) {
  const i = s ? s.i : 0, paintedBg = segsBg[i] || bg, img = segsPhoto[i];
  ctx.drawImage(paintedBg, 0, 0);
  if (!img) return;
  // stock photo behind the presenter: cover the wall area, slow Ken Burns with alternating pan
  const u = s ? clamp((t - s.start) / Math.max(1, s.end - s.start)) : 0;
  const kb = 1.04 + 0.1 * u, pan = (i % 2 ? 1 : -1) * 40 * (u - 0.5);
  const sc = Math.max(W / img.width, (FLOOR_Y + 60) / img.height) * kb;
  const iw = img.width * sc, ih = img.height * sc;
  ctx.save();
  ctx.beginPath(); ctx.rect(-200, -200, W + 400, FLOOR_Y + 200); ctx.clip();
  ctx.drawImage(img, (W - iw) / 2 + pan, (FLOOR_Y + 60 - ih) / 2, iw, ih);
  // warm grade so the photo sits with the cartoon, and a fade into the floor
  ctx.fillStyle = 'rgba(246,226,196,0.20)'; ctx.fillRect(-200, -200, W + 400, FLOOR_Y + 200);
  const g = ctx.createLinearGradient(0, FLOOR_Y - 220, 0, FLOOR_Y);
  g.addColorStop(0, 'rgba(60,35,20,0)'); g.addColorStop(1, 'rgba(60,35,20,0.45)');
  ctx.fillStyle = g; ctx.fillRect(-200, FLOOR_Y - 220, W + 400, 220);
  ctx.restore();
  ctx.strokeStyle = INK; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(-200, FLOOR_Y); ctx.lineTo(W + 200, FLOOR_Y); ctx.stroke();
}

window.renderFrame = (t) => {
  T = t; strokeId = 0;
  const cur = segs.find(s => t >= s.start && t < s.end) || segs[segs.length - 1];
  segs.forEach(s => (s.card.style.display = 'none'));
  const cam = cur ? cameraAt(cur, t) : { dx: 0, z: 1, fx: W / 2, fy: 1050 };
  // background: slower parallax, slightly oversized so whips never show an edge
  const bz = 1.22 + (cam.z - 1) * 0.4;
  ctx.setTransform(bz, 0, 0, bz, W / 2 * (1 - bz) + cam.dx * 0.35, 1050 * (1 - bz));
  drawBackdrop(cur, t);
  const ck = cur ? segsKind[cur.i] : kindOfBg;
  if (!(cur && segsPhoto[cur.i]) && (ck === 'nature' || ck === 'town' || ck === 'classical'))
    for (let i = 0; i < 2; i++) ctx.drawImage(clouds, ((i * 640 + t * 14) % 1600) - 520, 200 + i * 120, 520 * (0.8 + i * 0.3), 200 * (0.8 + i * 0.3));
  ctx.setTransform(cam.z, 0, 0, cam.z, cam.fx * (1 - cam.z) + (W / 2 - cam.fx) * (cam.z - 1) * 0.5 + cam.dx, cam.fy * (1 - cam.z));
  if (cur) updateSegment(cur, t);
  // film texture on top: grain re-rolls every 3 frames (on the 10 fps paper clock), plus a warm vignette
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.imageSmoothingEnabled = false; ctx.drawImage(GRAIN[Math.floor(t * 10) % GRAIN.length], 0, 0, W, H); ctx.imageSmoothingEnabled = true;
  ctx.drawImage(VIGNETTE, 0, 0);
  document.getElementById('cards').style.transform = `translateX(${cam.dx}px)`;
  document.getElementById('fill').style.width = `${clamp(t / cfg.total) * 100}%`;
};
window.sceneReady = true;
