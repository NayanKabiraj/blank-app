// Explainer scene (the only look of the channel): a whiteboard. Everything is drawn in marker, strokes draw
// themselves on while a hand holds the pen, headlines are handwritten, one smiling sun is carried from scene
// to scene, captions are white pills with a yellow highlighter on the keyword.
// Rendered frame by frame by ./render.cjs. Everything is a pure function of time t
// (no Math.random, Date or CSS animation) so the render can be split across parallel browsers.
// The plan's per-scene `graphic` (title, keyword, stat, steps, flow, build, cycle, race, compare, bars and the
// conversation scenes chat, quiz, myth, plus an optional `prop` icon) decides what is drawn; `keyword` timing
// drives the main beat. The accent colour follows the niche.
let W = 1080, H = 1920, LAND = false;                 // portrait Short by default; the documentary renders 1920x1080
const INTRO = 0.6, OUTRO = 0.3;
const PANEL_DX = 720, PANEL_DY = -470;                 // landscape: the 1080-wide diagram area is moved into the right-hand panel
const BG = '#fbfaf4', PANEL = '#ffffff', PANEL2 = '#ece9df', TEXT = '#1c1c1e', MUTED = '#6b6f76';
let BLUE = '#1f6feb';
const ORANGE = '#f26b21', SUN = '#ffd43b';
const GREEN = '#1f9d55', RED = '#e03131';
const NICHE_ACCENT = [[/body|health|medic/i, '#e0457b'], [/space|astro|universe/i, '#7a4df0'], [/money|financ|econom|india/i, '#1f9d55'],
  [/nature|animal|earth|environment/i, '#0f9f8a'], [/histor|human|mind|psych|brain/i, '#d97706']];
const tint = (hex, a) => `rgba(${parseInt(hex.slice(1, 3), 16)},${parseInt(hex.slice(3, 5), 16)},${parseInt(hex.slice(5, 7), 16)},${a})`;
const mix = (hex, k) => '#' + [1, 3, 5].map(i => Math.round(parseInt(hex.slice(i, i + 2), 16) * k).toString(16).padStart(2, '0')).join('');
const SPEC = ['#ff4d4d', '#ff9a3c', '#ffe14d', '#4ddb7a', '#3d9bff', '#9a6bff'];
const INK = TEXT;                                   // marker black
const FONT = '"Kalam", "Noto Sans", "Noto Sans Devanagari", cursive';   // handwriting, Latin + Devanagari
let pal = [BLUE, ORANGE, PANEL];                    // the prop icons read pal[0..2]
let cfg, ctx, segs = [], T = 0, strokeId = 0;

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

const segsPhoto = {}, segsBg = {}, segsKind = {};

// ------------------------------------------------------------------ pen: clean ink strokes
// pts: [[x,y],...]. o: {close, w, color, fill, p (draw-on progress 0..1), amp}
function pen(pts, o = {}) {
  const p = o.p ?? 1, id = o.seed ?? strokeId++;
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
  ctx.beginPath(); ctx.moveTo(out[0][0], out[0][1]); let lp = out[0];
  for (let i = 1; i < out.length && budget > 0; i++) {
    const l = seg[i - 1];
    if (l <= budget) { ctx.lineTo(out[i][0], out[i][1]); lp = out[i]; }
    else { const f = budget / l; lp = [lerp(out[i - 1][0], out[i][0], f), lerp(out[i - 1][1], out[i][1], f)]; ctx.lineTo(lp[0], lp[1]); }
    budget -= l;
  }
  ctx.stroke();
  if (p > 0 && p < 1) setTip(lp[0], lp[1]);                  // the hand follows the pen while a stroke is being drawn
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
function parseNumber(s) {
  const m = s.trim().match(/^(\D*?)(-?\d[\d,]*(?:\.\d+)?)(.*)$/);
  if (!m) return null;
  const raw = m[2], decimals = raw.includes('.') ? raw.split('.')[1].length : 0;
  const value = parseFloat(raw.replace(/,/g, ''));
  const isYear = !m[1].trim() && !m[3].trim() && decimals === 0 && value >= 1000 && value <= 2100;
  return { prefix: m[1], value, suffix: m[3].trim(), decimals, commas: raw.includes(','), isYear };
}
const fmt = (v, d, commas) => commas ? v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }) : v.toFixed(d);

// ------------------------------------------------------------------ small drawing helpers
let tip = null;                                              // where the pen is right now (screen coordinates), if a stroke is being drawn
function setTip(x, y) { const m = ctx.getTransform(); tip = [m.a * x + m.c * y + m.e, m.b * x + m.d * y + m.f]; }
function setFont(size, weight = 700) { ctx.font = `${weight} ${size}px ${FONT}`; }
function fitText(str, x, y, maxW, size, color, align = 'left', weight = 700, p = 1) {   // p < 1: the text is being written
  let f = size; setFont(f, weight);
  while (f > 28 && ctx.measureText(str).width > maxW) { f -= 2; setFont(f, weight); }
  const w = ctx.measureText(str).width, x0 = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x;
  ctx.save();
  if (p < 1) { ctx.beginPath(); ctx.rect(x0 - 10, y - f, (w + 20) * clamp(p), f * 2); ctx.clip(); }
  ctx.fillStyle = color; ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.fillText(str, x, y + f * 0.06);
  ctx.restore();
  if (p > 0 && p < 1) setTip(x0 + w * clamp(p), y + f * 0.35);
  return f;
}
function rrect(x, y, w, h, r) {
  ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}
function rrPts(x, y, w, h, r) {                              // a rounded rectangle as a polyline, for the pen
  r = Math.min(r, w / 2, h / 2); const pts = [], n = 4;
  const corner = (cx, cy, a0) => { for (let i = 0; i <= n; i++) { const a = a0 + (Math.PI / 2) * (i / n); pts.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); } };
  corner(x + w - r, y + r, -Math.PI / 2); corner(x + w - r, y + h - r, 0); corner(x + r, y + h - r, Math.PI / 2); corner(x + r, y + r, Math.PI);
  return pts;
}
function box(x, y, w, h, o = {}) {                           // hand-drawn rounded box: o = {fill, color, lw, r, p, seed}
  pen(rrPts(x, y, w, h, o.r ?? 24), { close: true, fill: o.fill, color: o.color || INK, w: o.lw ?? 5, p: o.p ?? 1, seed: o.seed, amp: 1.1 });
}
function dot(x, y, r, fill, glow = 0) {
  ctx.save(); ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fillStyle = fill; ctx.fill(); ctx.restore();
}
function line(x1, y1, x2, y2, p, color, w = 8, seed) {       // a marker line that draws itself on (p = 0..1)
  if (p <= 0) return;
  pen([[x1, y1], [x2, y2]], { p, color, w, seed, amp: 0.9 });
}
function arrow(x1, y1, x2, y2, p, color, w = 8, seed) {      // a line with an arrow head that appears at the end
  line(x1, y1, x2, y2, p, color, w, seed);
  const hp = clamp((p - 0.82) / 0.18); if (hp <= 0) return;
  const a = Math.atan2(y2 - y1, x2 - x1), L = 26;
  for (const d of [2.6, -2.6]) line(x2, y2, x2 + Math.cos(a + d) * L, y2 + Math.sin(a + d) * L, hp, color, w, (seed ?? 0) + (d > 0 ? 1 : 2));
}
function squiggle(x1, x2, y, p, color, seed, w = 8) {        // a hand-drawn underline
  const n = 6, pts = Array.from({ length: n + 1 }, (_, i) => [lerp(x1, x2, i / n), y + (i % 2 ? 7 : -5)]);
  pen(pts, { p, color, w, seed, amp: 0.8 });
}
const popS = (dt, cap = 1.12) => Math.min(cap, popAt(dt));   // measured pop-in with overshoot
const writeP = (t, t0, dur = 0.7) => clamp((t - t0) / dur);  // progress of a handwritten label

// ------------------------------------------------------------------ the guiding sun, carried between scenes
function orb(x, y, s, pulse) {
  ctx.save(); ctx.translate(x, y); const k = s * (1 + 0.16 * pulse); ctx.scale(k, k);
  ctx.rotate(T * 0.14);
  for (let i = 0; i < 8; i++) { const a = (i / 8) * Math.PI * 2; pen([[Math.cos(a) * 88, Math.sin(a) * 88], [Math.cos(a) * 124, Math.sin(a) * 124]], { color: ORANGE, w: 10, seed: 700 + i, amp: 1.4 }); }
  ctx.rotate(-T * 0.14);
  circle(0, 0, 66, { fill: SUN, color: INK, w: 7, seed: 720 });
  dot(-23, -9, 6.5, INK); dot(23, -9, 6.5, INK);
  pen(arcPts(0, 4, 28, 22, 0.25, Math.PI - 0.25, 10), { color: INK, w: 6, seed: 721, amp: 0.4 });
  ctx.restore();
}
const ANCHOR = {                                             // [x, y, scale] of the sun for each kind of scene
  title: [880, 700, 0.7], keyword: [880, 700, 0.7], stat: [880, 700, 0.7], steps: [900, 760, 0.7], flow: [900, 760, 0.7],
  race: [900, 700, 0.7], compare: [540, 740, 0.75], build: [900, 700, 0.7], cycle: [540, 990, 0.8],
  bars: [940, 250, 0.5], chat: [940, 250, 0.5], quiz: [940, 250, 0.5], myth: [940, 250, 0.5],
};
function orbPos(t, cur) {
  if (LAND) { const p = easeOutCubic(clamp((t - cur.start) / 0.7)); return [150, 150 + Math.sin(t * 1.4) * 8, 0.6 * (0.7 + 0.3 * p)]; }
  const a = ANCHOR[cur.kind] || ANCHOR.title, pa = cur.i > 0 ? (ANCHOR[segs[cur.i - 1].kind] || ANCHOR.title) : a;
  const p = easeOutCubic(clamp((t - cur.start) / 0.7));
  return [lerp(pa[0], a[0], p), lerp(pa[1], a[1], p), lerp(pa[2], a[2], p)];
}

// ------------------------------------------------------------------ the hand that holds the marker
function drawHand() {
  if (!tip) return;
  ctx.save(); ctx.translate(tip[0], tip[1]); ctx.rotate(-0.95);
  ctx.shadowColor = 'rgba(0,0,0,0.22)'; ctx.shadowBlur = 14; ctx.shadowOffsetY = 8;
  ctx.lineJoin = 'round'; ctx.lineWidth = 4; ctx.strokeStyle = INK;
  ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(26, -9); ctx.lineTo(26, 9); ctx.closePath(); ctx.fillStyle = INK; ctx.fill();   // the nib
  rrect(24, -15, 190, 30, 9); ctx.fillStyle = '#2d3340'; ctx.fill(); ctx.stroke();                                              // the marker
  rrect(170, -16, 52, 32, 9); ctx.fillStyle = BLUE; ctx.fill(); ctx.stroke();                                                  // the cap
  ctx.shadowColor = 'transparent';
  ctx.fillStyle = '#f3c9a6';
  for (const [cx, cy, rx, ry, rot] of [[120, 4, 58, 34, -0.1], [92, -22, 34, 15, 0.5], [138, 24, 30, 14, 0.15], [104, 20, 28, 13, 0.12]]) {
    ctx.beginPath(); ctx.ellipse(cx, cy, rx, ry, rot, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  }
  ctx.restore();
}

// ------------------------------------------------------------------ build one scene
const DIAGRAM_OK = { flow: g => g.items?.length >= 2, build: g => g.items?.length >= 2, cycle: g => g.items?.length >= 3,
                     race: g => g.items?.length === 2 && g.values?.length === 2 && Math.min(...g.values) > 0,
                     steps: g => g.items?.length >= 2, compare: g => g.items?.length === 2,
                     bars: g => g.items?.length >= 2 && g.values?.length >= g.items.length && Math.min(...g.values) > 0,
                     chat: g => g.items?.length >= 2, myth: g => g.items?.length === 2,
                     quiz: g => g.items?.length >= 2 && Number.isInteger(g.answer) && g.answer >= 0 && g.answer < g.items.length };
function buildSegment(seg, i, all) {
  const g = seg.graphic, kind = g.kind;
  const s = { ...seg, g, i, kind, last: i === all.length - 1, hl: g.headline || '', cap: g.caption || '' };
  if (kind === 'stat' && parseNumber(g.headline)) { s.num = parseNumber(g.headline); s.hl = g.caption || ''; s.cap = ''; }
  else if (DIAGRAM_OK[kind] && DIAGRAM_OK[kind](g)) { s.labels = g.items.slice(0, 4); s.vals = g.values || []; s.diagram = kind; s.answer = g.answer; }
  else { s.kind = kind === 'title' ? 'title' : 'keyword'; s.prop = PROPS[g.prop] ? g.prop : DEFAULT_PROP[s.kind]; }
  if (kind === 'stat' && !s.num) { s.kind = 'keyword'; s.prop = PROPS[g.prop] ? g.prop : 'coin'; }
  // the headline is handwritten: each word is revealed from left to right
  const ui = document.getElementById('ui');
  const h = document.createElement('div'); h.className = 'hl'; s.words = [];
  (s.hl || s.cap).split(' ').forEach((w, k, arr) => {
    const sp = document.createElement('span'); sp.className = 'w'; sp.textContent = w + (k < arr.length - 1 ? ' ' : ''); h.append(sp); s.words.push(sp);
  });
  if (!s.hl) h.style.display = 'none';
  ui.append(h); s.hlEl = h;
  if (s.hl && s.cap) { const c = document.createElement('div'); c.className = 'sub'; c.textContent = s.cap; ui.append(c); s.capEl = c; }
  // fit the headline into two lines (three in landscape), then place the caption under it
  h.style.display = 'block'; let size = LAND ? (s.hl.length <= 14 ? 100 : 86) : (s.hl.length <= 14 ? 104 : 92); h.style.fontSize = size + 'px';
  const maxLines = LAND ? 3.05 : 2.05;
  while (size > 52 && h.offsetHeight > size * 1.2 * maxLines) { size -= 4; h.style.fontSize = size + 'px'; }
  s.hlH = h.offsetHeight; h.style.display = 'none';
  s.hlTop = LAND ? Math.max(260, Math.round((H - s.hlH - (s.capEl ? 110 : 0)) / 2) - 40) : 350;
  if (s.capEl) s.capEl.style.top = (s.hlTop + s.hlH + 6) + 'px';
  return s;
}

// ------------------------------------------------------------------ scene drawing
function wrapLines(str, maxW, size, weight = 700) {          // greedy word wrap
  setFont(size, weight); const out = []; let cur = '';
  for (const w of str.split(' ')) { const t = cur ? cur + ' ' + w : w; if (cur && ctx.measureText(t).width > maxW) { out.push(cur); cur = w; } else cur = t; }
  if (cur) out.push(cur); return out;
}
function bodyTop(s) { if (LAND) return 640; return Math.max(640, s.hlTop + (s.hl ? s.hlH : 0) + (s.cap ? 90 : 0) + 50); }

function drawProp(s, t, u, pk) {
  const k = popS(u - 0.15) * (1 + 0.06 * pk);
  withT(540, 990, 2.5 * k, Math.sin(t * 1.3) * 0.04, () => PROPS[s.prop](clamp((u - 0.15) / 0.7)));
  if (s.kind === 'keyword') {                                 // a dashed marker ring around the key object
    ctx.save(); ctx.translate(540, 990); ctx.rotate(t * 0.5); ctx.strokeStyle = BLUE; ctx.lineWidth = 9; ctx.lineCap = 'round';
    ctx.setLineDash([46, 34]); ctx.beginPath(); ctx.arc(0, 0, 300 * clamp((u - 0.5) / 0.6), 0, Math.PI * 2); ctx.stroke(); ctx.restore();
  } else {                                                    // burst lines on the hook
    for (let j = 0; j < 8; j++) { const a = -Math.PI + (j / 7) * Math.PI; line(540 + Math.cos(a) * 330, 990 + Math.sin(a) * 330, 540 + Math.cos(a) * 395, 990 + Math.sin(a) * 395, clamp((u - 0.6 - j * 0.05) / 0.25), ORANGE, 11, 300 + j); }
  }
}
function drawStat(s, t, u, pk) {
  const c0 = s.hit ? Math.max(s.start, s.hit - 1.5) : s.start + 0.2, cu = t - c0;
  const p = s.num.isYear ? clamp(cu / 0.5) : easeOutCubic(clamp(cu / 1.4));
  const text = s.num.prefix + fmt(s.num.value * (s.num.isYear ? 1 : p), s.num.decimals, s.num.commas);
  const stamp = stampAt(t - (c0 + 1.4)) * (1 + 0.05 * pk);
  ctx.save(); ctx.translate(540, 930); ctx.scale(stamp, stamp);
  fitText(text, 0, 0, 900, 250, BLUE, 'center', 700);
  ctx.restore();
  if (s.num.suffix) fitText(s.num.suffix, 540, 1100, 860, 80, INK, 'center', 700);
  ellipse(540, 940, 400, 190, { color: ORANGE, w: 9, p: clamp((t - (c0 + 1.3)) / 0.7), seed: 330 }, -0.03);      // circled for emphasis
  const lit = Math.round(p * 10);                             // ten marker dots fill up while the number counts
  for (let j = 0; j < 10; j++) { circle(250 + j * 64, 1260, 18, { fill: j < lit ? ORANGE : '#ffffff', color: INK, w: 5, seed: 340 + j, amp: 0.4 }); }
}
function drawChain(s, t, u, A, pk) {                          // steps (all labels visible, active one lit) and flow (nodes appear, dots flow)
  const n = s.labels.length, x = 215, gap = n > 1 ? Math.min(165, 500 / (n - 1)) : 0, y0 = 990 - ((n - 1) * gap) / 2, flow = s.diagram === 'flow';
  const t0 = s.start + INTRO * 0.8, D = Math.max(0.8, s.end - OUTRO - t0);
  const appear = j => t0 + (j * D) / (n + 0.6);
  const active = flow ? Math.min(n - 1, Math.max(-1, Math.floor((t - t0) / (D / (n + 0.6))))) : Math.max(-1, Math.min(n - 1, Math.floor((t - s.start - INTRO) / Math.max(0.3, (s.end - OUTRO - s.start - INTRO) / n))));
  for (let j = 0; j < n; j++) {
    const y = y0 + j * gap;
    if (j < n - 1) {
      const ep = flow ? clamp((t - appear(j + 1) + 0.25) / 0.45) : clamp((u - 0.3 - j * 0.12) / 0.4);
      arrow(x, y + 56, x, y + gap - 60, ep, flow || j < active ? BLUE : '#9aa0a6', 8, 400 + j * 4);
      if (flow && ep >= 1) for (let q = 0; q < 3; q++) dot(x, y + 56 + (gap - 116) * ((t * 0.8 + q / 3) % 1), 11, ORANGE);
    }
    const a = flow ? clamp((t - appear(j)) / 0.35) : clamp((u - j * 0.1) / 0.4);
    if (a <= 0) continue;
    const on = j === active, done = j < active, r = 54 * popS(a * 0.7) * (on ? 1 + 0.06 * pk : 1);
    circle(x, y, r, { fill: on ? BLUE : done ? tint(BLUE, 0.22) : '#ffffff', color: INK, w: 6, p: clamp(a * 1.6), seed: 420 + j * 3, amp: 0.8 });
    fitText(String(j + 1), x, y + 2, 80, 54, on ? '#ffffff' : INK, 'center', 700);
    fitText(s.labels[j], x + 96, y + 2, 700, 70, on ? INK : done ? '#3b3f46' : MUTED, 'left', 700, writeP(t, appear(j) + 0.1, 0.55));
  }
}
function drawRace(s, t, u, pk) {
  const vmax = Math.max(...s.vals), x0 = 110, x1 = 770, len = x1 - x0, gap = 0.34, ts = s.start + INTRO + 0.2;
  s.labels.slice(0, 2).forEach((lab, j) => {
    const y = 880 + j * 250, col = j ? ORANGE : BLUE, speed = Math.max(4, 460 * s.vals[j] / vmax);
    fitText(lab, x0, y - 78, 800, 64, INK, 'left', 700, writeP(t, s.start + 0.4 + j * 0.2, 0.5));
    line(x0, y, x1, y, clamp((u - 0.2) / 0.4), '#9aa0a6', 8, 500 + j * 2); line(x1 + 8, y - 44, x1 + 8, y + 44, clamp((u - 0.5) / 0.3), INK, 10, 510 + j);
    const m = Math.floor((t - ts) / gap);
    for (let q = Math.max(0, m - 40); q <= m; q++) { const px = x0 + speed * (t - (ts + q * gap)); if (px >= x0 && px <= x1) dot(px, y, 15, col); }
    const arrived = t < ts ? 0 : Math.max(0, Math.floor((t - ts - len / speed) / gap) + 1);
    circle(x1 + 96, y, 54 * (1 + 0.1 * pk), { fill: col, color: INK, w: 6, seed: 520 + j, amp: 0.6 });
    fitText(String(arrived), x1 + 96, y + 3, 90, 54, '#ffffff', 'center', 700);
  });
}
function drawBuild(s, t, u, pk) {
  const n = s.labels.length, t0 = s.start + INTRO * 0.8, D = Math.max(0.8, s.end - OUTRO - t0);
  const h = Math.min(124, (540 - 12 * (n - 1)) / n);
  s.labels.forEach((lab, j) => {
    const at = t0 + (j * D) / (n + 0.4), a = clamp((t - at) / 0.45); if (a <= 0) return;
    const top = j === n - 1 ? t >= at : t >= at && t < t0 + ((j + 1) * D) / (n + 0.4);
    const w = 800 - j * 24, x = 540 - w / 2, y = 1260 - (j + 1) * (h + 12) + 12 - (1 - popS(a)) * 150;
    ctx.save(); ctx.globalAlpha *= clamp(a * 2.2);
    box(x, y, w, h, { fill: top ? BLUE : tint(BLUE, 0.12), lw: 6, p: clamp(a * 1.4), seed: 600 + j * 3 });
    fitText(lab, 540, y + h / 2 + 2, w - 60, 62, top ? '#ffffff' : INK, 'center', 700, writeP(t, at + 0.1, 0.5)); ctx.restore();
  });
}
function drawCycle(s, t, u, pk) {
  const n = s.labels.length, cx = 540, cy = 990, R = 290, t0 = s.start + INTRO * 0.8, D = Math.max(0.8, s.end - OUTRO - t0);
  const ang = j => -Math.PI / 2 + (j * Math.PI * 2) / n, ring = clamp((t - t0) / 0.9);
  pen(arcPts(cx, cy, R, R, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2, 72).slice(0, -1), { p: ring, color: '#9aa0a6', w: 8, seed: 700, close: true });
  const lap = Math.max(2.4, D / 1.5), ta = ang(0) + (Math.max(0, t - t0 - 0.6) / lap) * Math.PI * 2;
  const activeIdx = Math.floor((((ta + Math.PI / 2) / (Math.PI * 2)) % 1) * n + 1e-6) % n;
  if (t > t0 + 0.6) dot(cx + Math.cos(ta) * R, cy + Math.sin(ta) * R, 20, ORANGE);
  s.labels.forEach((lab, j) => {
    const a = clamp((t - t0 - j * 0.25) / 0.4); if (a <= 0) return;
    const px = cx + Math.cos(ang(j)) * R, py = cy + Math.sin(ang(j)) * R, on = t > t0 + 0.6 && j === activeIdx;
    const w = 340 * popS(a) * (on ? 1 + 0.06 * pk : 1), h = 96 * popS(a);
    box(px - w / 2, py - h / 2, w, h, { fill: on ? BLUE : '#ffffff', lw: 6, seed: 710 + j * 3, p: clamp(a * 1.5), r: 30 });
    fitText(lab, px, py + 2, w - 36, 54, on ? '#ffffff' : INK, 'center', 700, writeP(t, t0 + j * 0.25 + 0.1, 0.5));
  });
}
function drawCompare(s, t, u, pk) {
  const vals = s.vals.length === 2 && Math.max(...s.vals) > 0 ? s.vals : [1, 1], mx = Math.max(...vals);
  const R = vals.map(v => 120 + 90 * Math.sqrt(v / mx)), xs = [290, 790], y = 1040;      // disc area follows the value
  const grow = [popS(u - 0.25), popS(u - 0.55)];
  [0, 1].forEach(j => {
    circle(xs[j], y, R[j] * grow[j] * (1 + 0.05 * pk), { fill: tint(j ? ORANGE : BLUE, 0.35), color: j ? ORANGE : BLUE, w: 9, p: clamp((u - 0.25 - j * 0.3) / 0.7), seed: 800 + j * 7 });
    fitText(s.labels[j], xs[j], y + R[j] + 74, 440, 64, INK, 'center', 700, writeP(t, s.start + 0.8 + j * 0.3, 0.5));
  });
  const p = clamp((u - 1.0) / 0.7);                           // the arc that joins the two
  pen(Array.from({ length: 21 }, (_, q) => { const f = q / 20; return [lerp(xs[0], xs[1], f), y - R[0] - 40 - Math.sin(Math.PI * f) * 90]; }), { p, color: INK, w: 7, seed: 830 });
}
function drawBars(s, t, u, pk) {
  const n = s.labels.length, vmax = Math.max(...s.vals), top = bodyTop(s), pitch = Math.min(170, (1330 - top) / n), t0 = s.start + INTRO * 0.8;
  const cols = [BLUE, ORANGE, GREEN, '#7a4df0'];
  s.labels.forEach((lab, j) => {
    const a = clamp((t - t0 - j * 0.3) / 0.4); if (a <= 0) return;
    const y = top + j * pitch, grow = easeOutCubic(clamp((t - t0 - j * 0.3 - 0.15) / 0.9)), w = 700 * (s.vals[j] / vmax);
    fitText(lab, 110, y, 820, 60, INK, 'left', 700, writeP(t, t0 + j * 0.3, 0.45));
    if (w * grow > 6) box(110, y + 36, Math.max(40, w * grow), 56, { fill: tint(cols[j % 4], 0.55), color: cols[j % 4], lw: 6, r: 14, seed: 900 + j * 3, amp: 0.8 });
    const v = s.vals[j] * grow, dec = Number.isInteger(s.vals[j]) ? 0 : 1;
    fitText(fmt(v, dec, s.vals[j] >= 10000), 110 + Math.max(40, w * grow) + 22, y + 66, 260, 58, INK, 'left', 700);
  });
}
function drawChat(s, t, u, pk) {
  const n = s.labels.length, t0 = s.start + INTRO * 0.8, D = Math.max(1.2, s.end - OUTRO - t0), step = D / (n + 0.4), size = 54;
  let y = bodyTop(s);
  const boxes = s.labels.map(lab => { const lines = wrapLines(lab, 650, size), h = lines.length * 66 + 46; return { lines, h }; });
  const total = boxes.reduce((q, b) => q + b.h + 26, 0), scale = total > 1340 - y ? (1340 - y) / total : 1;
  boxes.forEach((b, j) => {
    const at = t0 + j * step, a = clamp((t - at) / 0.35), me = j % 2 === 1, h = b.h * scale, w = 740 * scale;
    const x = me ? 1000 - w : 80, tt = at - 0.55;
    if (t > tt && t < at) {                                      // typing dots before the reply
      const dx = me ? 1000 - 190 : 80; box(dx, y, 190, 84, { fill: me ? tint(BLUE, 0.2) : '#ffffff', lw: 5, r: 42, seed: 950 + j * 5 });
      for (let q = 0; q < 3; q++) dot(dx + 55 + q * 40, y + 42 - Math.abs(Math.sin(t * 9 + q * 0.9)) * 10, 9, INK);
    }
    if (a > 0) {
      const k = popS(a * 0.7, 1.06);
      ctx.save(); ctx.translate(me ? 1000 : 80, y + h); ctx.scale(k, k); ctx.translate(me ? -1000 : -80, -(y + h));
      box(x, y, w, h, { fill: me ? tint(BLUE, 0.2) : '#ffffff', lw: 5, r: 38, seed: 960 + j * 5, p: clamp(a * 1.6) });
      ctx.fillStyle = INK; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; setFont(size * scale, 700);
      ctx.save(); ctx.beginPath(); ctx.rect(x, y, w * clamp((t - at - 0.05) / 0.5), h); ctx.clip();
      b.lines.forEach((ln, q) => ctx.fillText(ln, x + 36, y + 23 * scale + 33 * scale + q * 66 * scale)); ctx.restore();
      ctx.restore();
    }
    y += h + 26 * scale;
  });
}
function drawQuiz(s, t, u, pk) {
  const n = s.labels.length, top = bodyTop(s), h = Math.min(120, (1250 - top) / n - 20), t0 = s.start + INTRO;
  const R = Math.min(s.end - 0.9, Math.max(s.start + 2.0, s.hit && s.hit > s.start + 2.0 ? s.hit : s.start + (s.end - s.start) * 0.68));
  const rev = clamp((t - R) / 0.35);
  s.labels.forEach((lab, j) => {
    const a = clamp((t - t0 - j * 0.14) / 0.35); if (a <= 0) return;
    const right = j === s.answer, y = top + j * (h + 20), k = popS(a * 0.7) * (right && rev > 0 ? 1 + 0.05 * Math.sin(rev * Math.PI) : 1);
    ctx.save(); ctx.translate(540, y + h / 2); ctx.scale(k, k); ctx.translate(-540, -(y + h / 2));
    ctx.globalAlpha *= right || rev === 0 ? clamp(a * 2) : clamp(a * 2) * (1 - 0.6 * rev);
    box(110, y, 860, h, { fill: right && rev > 0 ? tint(GREEN, 0.28) : '#ffffff', color: right && rev > 0 ? GREEN : INK, lw: right && rev > 0 ? 8 : 5, r: 34, seed: 1000 + j * 4, p: clamp(a * 1.5) });
    circle(172, y + h / 2, h * 0.34, { fill: right && rev > 0 ? GREEN : PANEL2, color: INK, w: 5, seed: 1002 + j * 4, amp: 0.5 });
    fitText(String.fromCharCode(65 + j), 172, y + h / 2 + 2, 60, 42, right && rev > 0 ? '#ffffff' : INK, 'center', 700);
    fitText(lab, 236, y + h / 2 + 2, 690, 58, INK, 'left', 700, writeP(t, t0 + j * 0.14 + 0.1, 0.5));
    if (right && rev > 0) pen([[880, y + h / 2], [915, y + h / 2 + 30], [960, y + h / 2 - 34]], { color: GREEN, w: 14, p: rev, seed: 1100, amp: 0.6 });   // the tick
    ctx.restore();
  });
  if (t < R && t > t0 + 0.6) {                                   // countdown ring while the viewer thinks
    const left = R - t, cy = Math.min(1380, top + n * (h + 20) + 70);
    ctx.save(); ctx.lineWidth = 9; ctx.strokeStyle = PANEL2; ctx.beginPath(); ctx.arc(540, cy, 46, 0, Math.PI * 2); ctx.stroke();
    ctx.strokeStyle = ORANGE; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(540, cy, 46, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * clamp(left / (R - t0))); ctx.stroke(); ctx.restore();
    fitText(String(Math.max(1, Math.ceil(left))), 540, cy + 2, 60, 52, INK, 'center', 700);
  }
}
function drawMyth(s, t, u, pk) {
  const top = bodyTop(s), cw = 880, ch = 250, x = 100, strike = s.start + Math.max(1.0, (s.hit ? s.hit - s.start : (s.end - s.start) * 0.42));
  const sp = clamp((t - strike) / 0.45), fact = clamp((t - strike - 0.35) / 0.4);
  const a = clamp((u - 0.35) / 0.4);
  ctx.save(); ctx.globalAlpha *= clamp(a * 2) * (1 - 0.3 * sp);
  box(x, top, cw, ch, { fill: tint(RED, 0.08), color: RED, lw: 6, seed: 1200, p: clamp(a * 1.4) });
  box(x + 36, top - 26, 160, 52, { fill: RED, color: RED, lw: 4, r: 26, seed: 1201 }); fitText(cfg.lang === 'hi' ? 'मिथक' : 'MYTH', x + 116, top, 140, 34, '#ffffff', 'center', 700);
  const ml = wrapLines(s.labels[0], cw - 90, 60, 700); setFont(60, 700); ctx.fillStyle = INK; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ml.forEach((ln, q) => ctx.fillText(ln, x + cw / 2, top + ch / 2 + 8 + (q - (ml.length - 1) / 2) * 72));
  if (sp > 0) { const lw = Math.max(...ml.map(l => ctx.measureText(l).width)) + 60, cy = top + ch / 2 + 8; line(x + cw / 2 - lw / 2, cy, x + cw / 2 + lw / 2, cy - 6, sp, RED, 13, 1210); line(x + cw / 2 - lw / 2 + 20, cy + 22, x + cw / 2 + lw / 2 - 20, cy + 14, clamp(sp * 1.4 - 0.4), RED, 11, 1211); }
  ctx.restore();
  const y2 = top + ch + 90, k = fact > 0 ? stampAt(t - (strike + 0.35)) : 0;
  ctx.save(); ctx.translate(540, y2 + ch / 2); ctx.scale(Math.max(0.01, k), Math.max(0.01, k)); ctx.translate(-540, -(y2 + ch / 2)); ctx.globalAlpha *= clamp(fact * 2);
  box(x, y2, cw, ch, { fill: tint(GREEN, 0.16), color: GREEN, lw: 8, seed: 1220 });
  box(x + 36, y2 - 26, 160, 52, { fill: GREEN, color: GREEN, lw: 4, r: 26, seed: 1221 }); fitText(cfg.lang === 'hi' ? 'सच' : 'FACT', x + 116, y2, 140, 34, '#ffffff', 'center', 700);
  const fl = wrapLines(s.labels[1], cw - 90, 60, 700); setFont(60, 700); ctx.fillStyle = INK; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  fl.forEach((ln, q) => ctx.fillText(ln, x + cw / 2, y2 + ch / 2 + 8 + (q - (fl.length - 1) / 2) * 72));
  ctx.restore();
}
function drawBackdrop(s, t, u) {                                 // a faint doodle motif that changes from scene to scene
  ctx.save(); ctx.globalAlpha *= 0.09; const m = s.i % 4; ctx.fillStyle = INK; ctx.strokeStyle = INK;
  if (m === 1) { for (let x = 60; x < W; x += 90) for (let y = 60; y < H - 100; y += 90) { ctx.beginPath(); ctx.arc(x + ((t * 6) % 90), y, 3, 0, Math.PI * 2); ctx.fill(); } }
  else if (m === 2) { ctx.lineWidth = 3; for (let r = 1; r <= 6; r++) { const rr = r * 170 + ((t * 20) % 170) - 170; if (rr > 0) { ctx.beginPath(); ctx.arc(W / 2, H / 2, rr, 0, Math.PI * 2); ctx.stroke(); } } }
  else if (m === 3) { ctx.lineWidth = 3; for (let x = -1920 + ((t * 24) % 120); x < W; x += 120) { ctx.beginPath(); ctx.moveTo(x, H); ctx.lineTo(x + H, 0); ctx.stroke(); } }
  ctx.restore();
}
function drawCaptions(t) {
  const c = (cfg.captions || []).find(c => t >= c.start && t < c.end); if (!c) return;
  const a = clamp((t - c.start) / 0.14), words = c.words;
  let size = 74; setFont(size, 700);
  const text = words.map(w => w.t).join(' ');
  const capW = LAND ? 1500 : 840, capY = LAND ? 990 : 1440, cx0 = W / 2;
  if (LAND) { size = 62; setFont(size, 700); }
  while (size > 40 && ctx.measureText(text).width > capW) { size -= 2; setFont(size, 700); }
  const w = ctx.measureText(text).width + 90, h = size + 56, x = cx0 - w / 2, y = capY - h / 2 + (1 - a) * 14;
  ctx.save(); ctx.globalAlpha = a;
  ctx.shadowColor = 'rgba(0,0,0,0.18)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 6;
  rrect(x, y, w, h, 36); ctx.fillStyle = '#ffffff'; ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.lineWidth = 5; ctx.strokeStyle = INK; ctx.stroke();
  ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  let cx = cx0 - (w - 90) / 2;
  words.forEach(wd => {
    const ww = ctx.measureText(wd.t).width;
    if (wd.kw) { ctx.fillStyle = '#ffe14d'; rrect(cx - 8, y + h / 2 - size * 0.5, ww + 16, size * 0.95, 10); ctx.fill(); }   // yellow highlighter on the keyword
    ctx.fillStyle = INK; ctx.fillText(wd.t, cx, y + h / 2 + size * 0.06); cx += ctx.measureText(wd.t + ' ').width;
  });
  ctx.restore();
}

function drawHook(t) {                                          // the hook teaser for the first 3 seconds (Shorts): a highlighter box
  if (!cfg.hook || LAND || t > 3.0) return;
  const a = clamp(t / 0.25) * clamp((3.0 - t) / 0.35), k = 0.94 + 0.06 * clamp(t / 0.25);
  let size = 76; setFont(size, 700);
  while (size > 44 && ctx.measureText(cfg.hook).width > 880) { size -= 2; setFont(size, 700); }
  const w = ctx.measureText(cfg.hook).width + 90, h = size + 50, x = W / 2 - w / 2, y = 120;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(W / 2, y + h / 2); ctx.scale(k, k); ctx.translate(-W / 2, -(y + h / 2));
  rrect(x, y, w, h, 22); ctx.fillStyle = '#ffe14d'; ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = INK; ctx.stroke();
  ctx.fillStyle = INK; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(cfg.hook, W / 2, y + h / 2 + size * 0.06);
  ctx.restore();
}

function updateSegment(s, t) {
  const u = t - s.start, enter = clamp(u / INTRO), exit = clamp((s.end - t) / OUTRO), A = clamp(enter * 2.2) * (s.last ? 1 : exit);
  const pk = s.hit ? clamp(1 - Math.abs(t - (s.hit - 0.03)) / 0.22) : 0;   // lands ~3 frames before the keyword
  // the headline is written word by word
  if (s.hl) {
    s.hlEl.style.display = 'block'; s.hlEl.style.top = s.hlTop + 'px'; s.hlEl.style.opacity = String(A);
    s.words.forEach((w, j) => { const a = clamp((u - 0.1 - j * 0.16) / 0.38); w.style.clipPath = `inset(-10% ${(1 - a) * 102}% -10% -2%)`; });
    if (s.capEl) { s.capEl.style.display = 'block'; s.capEl.style.opacity = String(clamp((u - 0.7) / 0.4) * A); }
  }
  ctx.save(); ctx.globalAlpha = A;
  if (s.hl) { const ux = LAND ? 90 : 540 - 190; squiggle(ux, ux + 380, s.hlTop + s.hlH + (s.capEl ? 80 : 14), clamp((u - 0.5 - s.words.length * 0.12) / 0.5), BLUE, 40 + s.i); }
  drawBackdrop(s, t, u);
  const [ox, oy, os] = orbPos(t, s); orb(ox, oy, os * popS(u + 0.3, 1.0), pk);
  if (LAND) ctx.translate(PANEL_DX, PANEL_DY);
  if (s.num) drawStat(s, t, u, pk);
  else if (s.diagram === 'flow' || s.diagram === 'steps') drawChain(s, t, u, A, pk);
  else if (s.diagram === 'race') drawRace(s, t, u, pk);
  else if (s.diagram === 'build') drawBuild(s, t, u, pk);
  else if (s.diagram === 'cycle') drawCycle(s, t, u, pk);
  else if (s.diagram === 'compare') drawCompare(s, t, u, pk);
  else if (s.diagram === 'bars') drawBars(s, t, u, pk);
  else if (s.diagram === 'chat') drawChat(s, t, u, pk);
  else if (s.diagram === 'quiz') drawQuiz(s, t, u, pk);
  else if (s.diagram === 'myth') drawMyth(s, t, u, pk);
  else drawProp(s, t, u, pk);
  ctx.restore();
}

// ------------------------------------------------------------------ public API
window.setup = async (config) => {
  cfg = config;
  const hit = NICHE_ACCENT.find(([re]) => re.test(cfg.niche || ''));
  if (hit) BLUE = hit[1];
  pal = [BLUE, ORANGE, PANEL];
  document.body.lang = cfg.lang === 'hi' ? 'hi' : 'en';
  LAND = cfg.layout === 'landscape';
  if (LAND) { W = 1920; H = 1080; document.getElementById('ui').classList.add('land'); }
  const cv = document.getElementById('cv'); cv.width = W; cv.height = H;
  for (const el of [document.documentElement, document.body, cv]) { el.style.width = W + 'px'; el.style.height = H + 'px'; }
  ctx = cv.getContext('2d');
  await Promise.all([document.fonts.load('700 40px Kalam'), document.fonts.load('400 40px Kalam'),
                     document.fonts.load('700 40px Kalam', 'आ'), document.fonts.load('400 40px Kalam', 'आ')]);
  segs = cfg.segments.map((s, i, all) => buildSegment(s, i, all));
  await document.fonts.ready;
};
window.renderFrame = (t) => {
  T = t; strokeId = 0; tip = null;
  const cur = segs.find(s => t >= s.start && t < s.end) || segs[segs.length - 1];
  segs.forEach(s => { s.hlEl.style.display = 'none'; if (s.capEl) s.capEl.style.display = 'none'; });
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
  ctx.fillStyle = BG; ctx.fillRect(0, 0, W, H);
  const g = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.15, W / 2, H / 2, Math.max(W, H) * 0.85);   // a soft board vignette
  g.addColorStop(0, 'rgba(120,110,90,0)'); g.addColorStop(0.45, 'rgba(120,110,90,0.02)'); g.addColorStop(0.75, 'rgba(120,110,90,0.05)'); g.addColorStop(1, 'rgba(120,110,90,0.10)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  if (cur) updateSegment(cur, t);
  drawHand();
  drawHook(t);
  drawCaptions(t);
};
window.sceneReady = true;
