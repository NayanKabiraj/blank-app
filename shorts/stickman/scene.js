// 2D stickman explainer scene, rendered frame by frame by ../cartoon3d/render.cjs.
// A hand-drawn look made entirely in code: black marker strokes that "boil" (redraw with a new
// wobble 8 times a second) on off-white paper, one stick figure who reacts to the narration,
// doodle props that draw themselves on, and one accent colour per niche.
// Everything is a pure function of time t (no Math.random, Date or CSS animation), so the
// render can be split across parallel browsers. Text is HTML so Devanagari is shaped correctly.

const W = 1080, H = 1920, INTRO = 0.6, OUTRO = 0.35;
const INK = '#1b1b1b', PAPER = '#fbfaf5', GROUND = 1255;
// [accent, accent2, soft accent (highlighter)]
const PALETTES = [
  ['#e63946', '#1d70b8', 'rgba(230,57,70,0.28)'],
  ['#2a9d8f', '#e76f51', 'rgba(42,157,143,0.28)'],
  ['#1d70b8', '#f4a261', 'rgba(29,112,184,0.25)'],
  ['#f77f00', '#6a4c93', 'rgba(247,127,0,0.30)'],
  ['#6a4c93', '#2a9d8f', 'rgba(106,76,147,0.25)'],
  ['#d62828', '#2a9d8f', 'rgba(255,214,10,0.55)'],
];

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, k) => a + (b - a) * k;
const easeOutBack = x => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const easeOutCubic = x => 1 - Math.pow(1 - x, 3);
const easeInOut = x => (x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2);
const hash = s => { let h = 7; for (const c of s) h = (h * 31 + c.charCodeAt(0)) >>> 0; return h; };
const rnd = n => { const x = Math.sin(n * 12.9898 + 78.233) * 43758.5453; return x - Math.floor(x); };

let cfg, pal, ctx, segs = [], T = 0, strokeId = 0;

// ------------------------------------------------------------------ pen: wobbly marker strokes
// pts: [[x,y],...]. o: {close, w, color, fill, p (draw-on progress 0..1), amp}
function pen(pts, o = {}) {
  const p = o.p ?? 1, id = strokeId++;
  if (p <= 0 || pts.length < 2) return;
  const boil = Math.floor(T * 8), amp = o.amp ?? 2.2;
  const src = o.close ? [...pts, pts[0]] : pts;
  // subdivide and wobble perpendicular to each segment
  const out = [];
  let k = 0;
  for (let i = 0; i < src.length - 1; i++) {
    const [x1, y1] = src[i], [x2, y2] = src[i + 1];
    const len = Math.hypot(x2 - x1, y2 - y1), n = Math.max(1, Math.round(len / 16));
    const nx = -(y2 - y1) / (len || 1), ny = (x2 - x1) / (len || 1);
    for (let j = 0; j < n; j++, k++) {
      const f = j / n, d = (rnd(id * 131 + k * 7 + boil * 977) - 0.5) * 2 * amp;
      out.push([x1 + (x2 - x1) * f + nx * d, y1 + (y2 - y1) * f + ny * d]);
    }
  }
  const last = src[src.length - 1];
  out.push(o.close ? out[0] : [last[0], last[1]]);
  if (o.fill) {
    ctx.save(); ctx.globalAlpha *= clamp(p * 1.6 - 0.3); ctx.fillStyle = o.fill;
    ctx.beginPath(); out.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.fill(); ctx.restore();
  }
  // draw-on: cut the path at p of its length
  let total = 0; const seg = [];
  for (let i = 1; i < out.length; i++) { const l = Math.hypot(out[i][0] - out[i - 1][0], out[i][1] - out[i - 1][1]); seg.push(l); total += l; }
  let budget = total * clamp(p);
  ctx.strokeStyle = o.color || INK; ctx.lineWidth = o.w ?? 7; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
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

// ------------------------------------------------------------------ doodle props (same names as the 3D style)
// Each draws in a box of about ±100 around the origin. p = draw-on progress.
const PROPS = {
  star: p => pen(Array.from({ length: 10 }, (_, i) => { const r = i % 2 ? 40 : 92, a = -Math.PI / 2 + i * Math.PI / 5; return [Math.cos(a) * r, Math.sin(a) * r]; }), { close: true, fill: '#ffd166', p }),
  bulb: p => {
    circle(0, -25, 62, { fill: '#fff3b0', p });
    pen([[-28, 35], [-26, 72], [26, 72], [28, 35]], { fill: '#cfcfcf', p });
    pen([[-22, 84], [22, 84]], { p });
    for (let i = 0; i < 5; i++) { const a = -Math.PI * (0.15 + i * 0.175); pen([[Math.cos(a) * 80, -25 + Math.sin(a) * 80], [Math.cos(a) * 100, -25 + Math.sin(a) * 100]], { p, color: pal[0], w: 6 }); }
  },
  coin: p => { circle(0, 0, 82, { fill: '#ffd166', p }); circle(0, 0, 58, { p, w: 5 }); pen([[0, -30], [0, 30]], { p, w: 8 }); },
  planet: p => { circle(0, 0, 60, { fill: pal[1], p }); ellipse(0, 0, 108, 26, { p, color: pal[0], w: 8 }, -0.35); },
  globe: p => {
    circle(0, 0, 82, { fill: '#bde0fe', p }); ellipse(0, 0, 34, 82, { p, w: 5 });
    pen([[-82, 0], [82, 0]], { p, w: 5 }); pen(arcPts(0, -40, 70, 10, 0, Math.PI, 12), { p, w: 4 }); pen(arcPts(0, 40, 70, 10, Math.PI, Math.PI * 2, 12), { p, w: 4 });
  },
  phone: p => { rect(-52, -95, 104, 190, { fill: '#e0e0e0', p }); rect(-38, -76, 76, 136, { fill: '#bde0fe', p, w: 5 }); circle(0, 78, 8, { p, w: 4 }); },
  bank: p => {
    pen([[-100, -30], [0, -90], [100, -30]], { close: true, fill: pal[0], p });
    for (const x of [-66, -22, 22, 66]) pen([[x, -18], [x, 62]], { p, w: 9 });
    rect(-100, 66, 200, 20, { fill: '#e0e0e0', p });
  },
  rocket: p => {
    withT(0, 0, 1, 0.35, () => {
      pen([[0, -100], [32, -52], [32, 52], [-32, 52], [-32, -52]], { close: true, fill: '#ffffff', p });
      circle(0, -18, 15, { fill: '#bde0fe', p, w: 5 });
      pen([[-32, 20], [-58, 62], [-32, 52]], { close: true, fill: pal[0], p });
      pen([[32, 20], [58, 62], [32, 52]], { close: true, fill: pal[0], p });
      const f = 18 + Math.sin(T * 30) * 6;
      pen([[-20, 56], [0, 70 + f], [20, 56]], { close: true, fill: '#f77f00', p, w: 5 });
    });
  },
  brain: p => {
    pen(arcPts(0, 0, 1, 1, 0, Math.PI * 2, 48).slice(0, -1).map(([x, y]) => { const a = Math.atan2(y, x), r = 74 + 9 * Math.sin(a * 9); return [Math.cos(a) * r * 1.15, Math.sin(a) * r * 0.85]; }), { close: true, fill: '#ffc8dd', p });
    pen(Array.from({ length: 9 }, (_, i) => [Math.sin(i * 1.3) * 12, -55 + i * 14]), { p, w: 5 });
  },
  chip: p => {
    for (let i = -2; i <= 2; i++) for (const [x1, y1, x2, y2] of [[i * 22, -64, i * 22, -88], [i * 22, 64, i * 22, 88], [-64, i * 22, -88, i * 22], [64, i * 22, 88, i * 22]]) pen([[x1, y1], [x2, y2]], { p, w: 5 });
    rect(-64, -64, 128, 128, { fill: '#6c757d', p }); rect(-30, -30, 60, 60, { fill: pal[0], p, w: 5 });
  },
  heart: p => pen(Array.from({ length: 40 }, (_, i) => { const a = (i / 40) * Math.PI * 2; return [80 * Math.pow(Math.sin(a), 3) * 1.05, -(65 * Math.cos(a) - 26 * Math.cos(2 * a) - 10 * Math.cos(3 * a) - 5 * Math.cos(4 * a)) * 1.05 - 8]; }), { close: true, fill: '#ef476f', p }),
  clock: p => {
    circle(0, 0, 84, { fill: '#ffffff', p });
    for (let i = 0; i < 12; i++) { const a = (i / 12) * Math.PI * 2; pen([[Math.cos(a) * 68, Math.sin(a) * 68], [Math.cos(a) * 78, Math.sin(a) * 78]], { p, w: 5 }); }
    const a1 = T * 0.5 - Math.PI / 2, a2 = T * 3 - Math.PI / 2;
    pen([[0, 0], [Math.cos(a1) * 38, Math.sin(a1) * 38]], { p, w: 8 }); pen([[0, 0], [Math.cos(a2) * 60, Math.sin(a2) * 60]], { p, w: 6, color: pal[0] });
  },
  gear: p => {
    withT(0, 0, 1, T * 0.8, () => {
      pen(Array.from({ length: 40 }, (_, i) => { const a = (i / 40) * Math.PI * 2, r = i % 4 < 2 ? 88 : 66; return [Math.cos(a) * r, Math.sin(a) * r]; }), { close: true, fill: '#adb5bd', p, amp: 1.5 });
      circle(0, 0, 26, { fill: PAPER, p });
    });
  },
  atom: p => {
    for (let i = 0; i < 3; i++) ellipse(0, 0, 95, 30, { p, w: 6, color: i === 1 ? pal[0] : INK }, i * Math.PI / 3);
    circle(0, 0, 18, { fill: pal[0], p });
    const a = T * 3; const [ex, ey] = arcPts(0, 0, 95, 30, a, a, 1, Math.PI / 3)[0]; circle(ex, ey, 8, { fill: INK, p, w: 4 });
  },
  book: p => {
    pen([[0, -50], [-92, -66], [-92, 56], [0, 72]], { close: true, fill: '#ffffff', p });
    pen([[0, -50], [92, -66], [92, 56], [0, 72]], { close: true, fill: '#ffffff', p });
    for (let i = 0; i < 3; i++) { pen([[-75, -36 + i * 28], [-18, -26 + i * 28]], { p, w: 4 }); pen([[18, -26 + i * 28], [75, -36 + i * 28]], { p, w: 4 }); }
  },
  magnet: p => {
    pen([[-48, -78], [-48, 10], ...arcPts(0, 10, 48, 52, Math.PI, 0, 16).slice(1, -1), [48, 10], [48, -78]], { p, w: 30, color: '#e63946', amp: 1 });
    pen([[-48, -80], [-48, -52]], { p, w: 30, color: '#adb5bd', amp: 0.8 }); pen([[48, -80], [48, -52]], { p, w: 30, color: '#adb5bd', amp: 0.8 });
  },
  cloud: p => { [[0, -10, 52], [-55, 12, 38], [55, 12, 40], [-25, 26, 34], [25, 28, 34]].forEach(([x, y, r]) => circle(x, y, r, { fill: '#ffffff', p })); },
};
const DEFAULT_PROP = { title: 'star', keyword: 'bulb', stat: 'coin' };

// ------------------------------------------------------------------ the stick figure
// Angles: 0 = straight down, positive = towards screen right. [upper, lower] are absolute.
const POSES = {
  stand: { aL: [-0.3, -0.15], aR: [0.3, 0.15], lL: [-0.16, -0.1], lR: [0.16, 0.1], lean: 0, tilt: 0, face: 'smile' },
  point: { aL: [-0.3, -0.12], aR: [1.45, 1.6], lL: [-0.16, -0.1], lR: [0.16, 0.1], lean: 0.04, tilt: 0.05, face: 'grin' },
  wave: { aL: [-0.3, -0.12], aR: [2.4, 2.9], lL: [-0.16, -0.1], lR: [0.16, 0.1], lean: 0, tilt: -0.06, face: 'grin' },
  cheer: { aL: [-2.6, -2.95], aR: [2.6, 2.95], lL: [-0.3, -0.2], lR: [0.3, 0.2], lean: 0, tilt: 0, face: 'grin' },
  shrug: { aL: [-1.0, -2.5], aR: [1.0, 2.5], lL: [-0.16, -0.1], lR: [0.16, 0.1], lean: 0, tilt: 0.16, face: 'flat' },
  think: { aL: [-0.3, -0.12], aR: [0.35, -2.75], lL: [-0.16, -0.1], lR: [0.12, 0.05], lean: -0.03, tilt: -0.12, face: 'hmm' },
  shock: { aL: [-2.1, -2.7], aR: [2.1, 2.7], lL: [-0.28, -0.2], lR: [0.28, 0.2], lean: -0.08, tilt: 0, face: 'shock' },
  walk: { aL: [-0.3, -0.1], aR: [0.3, 0.1], lL: [-0.2, -0.1], lR: [0.2, 0.1], lean: 0.06, tilt: 0, face: 'smile' },
};
export const POSE_NAMES = Object.keys(POSES);
const lerpArr = (a, b, k) => a.map((v, i) => lerp(v, b[i], k));
function blendPose(a, b, k) {
  return { aL: lerpArr(a.aL, b.aL, k), aR: lerpArr(a.aR, b.aR, k), lL: lerpArr(a.lL, b.lL, k), lR: lerpArr(a.lR, b.lR, k),
           lean: lerp(a.lean, b.lean, k), tilt: lerp(a.tilt, b.tilt, k), face: k < 0.5 ? a.face : b.face };
}

function drawFigure(x, ground, pose, s, lift, facing) {
  const S = 1.3 * s, TH = 70 * S, SH = 68 * S, TORSO = 118 * S, UA = 62 * S, FA = 58 * S, HR = 38 * S;
  const t = T, P = { ...pose, aL: [...pose.aL], aR: [...pose.aR], lL: [...pose.lL], lR: [...pose.lR] };
  // life: breathing, wave and walk cycles
  const breathe = Math.sin(t * 3) * 0.04;
  P.aL = P.aL.map(v => v - breathe); P.aR = P.aR.map(v => v + breathe);
  if (pose.wave) P.aR[1] += Math.sin(t * 13) * 0.4;
  if (pose.walk) { const w = Math.sin(t * 11); P.lL = [-0.45 * w, -0.45 * w + 0.25]; P.lR = [0.45 * w, 0.45 * w + 0.25]; P.aL = [0.35 * w - 0.2, 0.35 * w - 0.05]; P.aR = [-0.35 * w + 0.2, -0.35 * w + 0.35]; }
  const dir = a => [Math.sin(a) * facing, Math.cos(a)];
  const legEnd = ([a1, a2]) => { const d1 = dir(a1), d2 = dir(a2); return [d1[0] * TH + d2[0] * SH, d1[1] * TH + d2[1] * SH]; };
  const footY = Math.max(legEnd(P.lL)[1], legEnd(P.lR)[1]);
  const hip = [x, ground - footY - lift - Math.abs(Math.sin(t * 3)) * 2];
  const tdir = [Math.sin(P.lean) * facing, -Math.cos(P.lean)];
  const neck = [hip[0] + tdir[0] * TORSO, hip[1] + tdir[1] * TORSO];
  const head = [neck[0] + tdir[0] * (HR + 6) + Math.sin(P.tilt) * 6 * facing, neck[1] + tdir[1] * (HR + 6)];
  const sh = [neck[0] + tdir[0] * -10, neck[1] + tdir[1] * -10];
  const limb = (o, [a1, a2], l1, l2) => { const d1 = dir(a1), d2 = dir(a2), m = [o[0] + d1[0] * l1, o[1] + d1[1] * l1]; pen([o, m, [m[0] + d2[0] * l2, m[1] + d2[1] * l2]], { w: 9 * s, amp: 1.6 }); };
  // shadow
  ctx.save(); ctx.fillStyle = 'rgba(0,0,0,0.08)'; ctx.beginPath(); ctx.ellipse(x, ground + 6, 70 * S * (1 - lift / 400), 10 * S, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  limb(hip, P.lL, TH, SH); limb(hip, P.lR, TH, SH);
  pen([hip, neck], { w: 9 * s, amp: 1.6 });
  limb(sh, P.aL, UA, FA); limb(sh, P.aR, UA, FA);
  circle(head[0], head[1], HR, { fill: '#ffffff', w: 8 * s, amp: 1.4 });
  // face
  const ex = 13 * S, ey = head[1] - 6 * S, lx = 6 * S * facing + head[0], blink = (t % 3.1) < 0.12;
  const eye = (cx) => {
    if (P.face === 'shock') circle(cx, ey, 7 * S, { fill: '#ffffff', w: 4, amp: 0.6 });
    if (blink) pen([[cx - 6 * S, ey], [cx + 6 * S, ey]], { w: 5, amp: 0.4 });
    else { ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(cx, ey, (P.face === 'shock' ? 3.5 : 5) * S, 0, Math.PI * 2); ctx.fill(); }
  };
  eye(lx - ex); eye(lx + ex);
  const my = head[1] + 16 * S;
  if (P.face === 'smile') pen(arcPts(lx, my - 8 * S, 13 * S, 9 * S, 0.3, Math.PI - 0.3, 8), { w: 5, amp: 0.5 });
  else if (P.face === 'grin') pen(arcPts(lx, my - 10 * S, 17 * S, 13 * S, 0.1, Math.PI - 0.1, 10), { close: true, w: 5, fill: '#ffffff', amp: 0.5 });
  else if (P.face === 'flat') pen([[lx - 12 * S, my], [lx + 12 * S, my + 2]], { w: 5, amp: 0.5 });
  else if (P.face === 'hmm') pen([[lx - 12 * S, my + 2], [lx + 4 * S, my - 1], [lx + 12 * S, my - 4]], { w: 5, amp: 0.5 });
  else if (P.face === 'shock') ellipse(lx, my, 7 * S, 10 * S, { w: 5, amp: 0.5 });
  if (P.face === 'shock') for (const k of [-1, 1]) pen([[head[0] + k * (HR + 14), head[1] - HR], [head[0] + k * (HR + 30), head[1] - HR - 18]], { w: 5, color: pal[0] });
  if (P.face === 'hmm') { ctx.save(); ctx.fillStyle = INK; ctx.font = `900 ${Math.round(48 * S)}px sans-serif`; ctx.fillText('?', head[0] + HR + 8, head[1] - HR + 4 * Math.sin(t * 4)); ctx.restore(); }
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
const HOME = { title: 300, keyword: 290, stat: 280, steps: 170, compare: 230 };

function buildSegment(seg, i, all) {
  const g = seg.graphic, kind = g.kind;
  const card = el('div', 'card'); card.style.display = 'none';
  const s = { ...seg, g, kind, card, i, last: i === all.length - 1, home: HOME[kind] ?? 300 };
  const headline = (txt, size) => { const h = el('div', 'head', txt); if (size) h.style.fontSize = size; card.append(h); s.hl = h; return h; };
  if (kind === 'stat' && parseNumber(g.headline)) {
    s.num = parseNumber(g.headline);
    s.big = el('div', 'big'); s.big.style.color = pal[0]; card.append(s.big);
    if (s.num.suffix) card.append(el('div', 'unit', s.num.suffix));
    if (g.caption) card.append(el('div', 'cap', g.caption));
  } else if (kind === 'steps' && g.items?.length >= 2) {
    headline(g.headline, '62px');
    const list = el('div', 'steps');
    s.items = g.items.slice(0, 4).map((txt, k) => { const d = el('div', 'step'); d.append(el('b', null, String(k + 1)), document.createTextNode(txt)); list.append(d); return d; });
    card.append(list);
    const n = s.items.length;
    s.pads = s.items.map((_, k) => 380 + (k * 480) / Math.max(1, n - 1));
  } else if (kind === 'compare' && g.items?.length === 2) {
    headline(g.headline, '70px');
    const row = el('div', 'cmp');
    g.items.forEach((txt, k) => { const d = el('div', null, txt); d.style.borderColor = k ? pal[1] : pal[0]; row.append(d); });
    card.append(row);
    const vals = g.values?.length === 2 && Math.max(...g.values) > 0 ? g.values : [1, 1];
    s.bars = vals.map(v => v / Math.max(...vals));
  } else {
    headline(g.headline, kind === 'title' ? '96px' : '88px');
    if (kind === 'keyword') s.hl.style.color = pal[0];
    if (g.caption) card.append(el('div', 'cap', g.caption));
    s.prop = PROPS[g.prop] ? g.prop : (DEFAULT_PROP[kind] || 'star');
  }
  // the figure's acting for this scene: keyframes [time offset, pose]
  const hold = Math.max(0.6, s.end - s.start - INTRO - OUTRO), mid = s.start + INTRO + hold * 0.45;
  const k = [];
  if (kind === 'title' && i === 0) k.push([s.start, 'shock'], [s.start + 1.3, 'point']);
  else if (s.last) k.push([s.start, 'wave'], [s.start + INTRO + hold * 0.6, 'cheer']);
  else if (kind === 'title') k.push([s.start, 'point']);
  else if (kind === 'keyword') k.push([s.start, 'think'], [mid, 'point']);
  else if (kind === 'stat') k.push([s.start, 'stand'], [s.start + 1.6, 'shock']);
  else if (kind === 'steps') k.push([s.start, 'point']);
  else if (kind === 'compare') k.push([s.start, 'point'], [s.start + INTRO + hold * 0.7, 'shrug']);
  else k.push([s.start, 'stand']);
  if (g.pose && POSES[g.pose]) k.splice(1, k.length, [s.start + Math.min(1.0, hold * 0.3), g.pose]);
  s.keys = k;
  if (i === 0) card.style.top = '470px'; // clear the hook text shown in the first seconds
  document.getElementById('cards').append(card);
  return s;
}

function poseAt(s, t) {
  let cur = POSES[s.keys[0][1]], prev = cur, since = 1e9;
  for (const [kt, name] of s.keys) if (t >= kt) { prev = cur; cur = { ...POSES[name], [name]: true }; since = t - kt; }
  const k = easeInOut(clamp(since / 0.28));
  return { ...blendPose(prev, cur, k), wave: cur.wave, walk: cur.walk };
}

// figure x position: walk from the previous scene's spot, hop between step pads
function figureAt(s, t) {
  const prevHome = s.i > 0 ? segs[s.i - 1].home : s.home;
  if (s.pads) {
    const holdStart = s.start + INTRO, holdEnd = s.end - OUTRO, n = s.pads.length;
    const per = Math.max(0.3, (holdEnd - holdStart) / n), HOP = 0.42;
    const stops = [{ t: -1e9, x: s.home }];
    s.pads.forEach((px, k) => stops.push({ t: holdStart + k * per, x: px }));
    for (let k = stops.length - 1; k >= 1; k--) {
      const a = stops[k - 1], b = stops[k];
      if (t >= b.t) return { x: b.x, lift: 0, walk: false, onPad: k - 1 };
      if (t >= b.t - HOP) { const p = clamp((t - (b.t - HOP)) / HOP); return { x: lerp(a.x, b.x, easeInOut(p)), lift: Math.sin(Math.PI * p) * 120, walk: false, onPad: k - 2 }; }
    }
  }
  const p = clamp((t - s.start) / 0.55);
  return { x: lerp(prevHome, s.home, easeInOut(p)), lift: 0, walk: p < 1 && Math.abs(prevHome - s.home) > 20, onPad: -1 };
}

function updateSegment(s, t) {
  const u = t - s.start;
  const enter = clamp(u / INTRO), exit = clamp((s.end - t) / OUTRO), k = easeOutBack(enter) * easeInOut(exit);
  const holdStart = s.start + INTRO, holdEnd = s.end - OUTRO;
  s.card.style.display = 'block';
  s.card.style.opacity = String(clamp(enter * 2) * exit);
  s.card.style.transform = `translateY(${(1 - enter) * 40}px) rotate(${(1 - k) * -3}deg) scale(${0.85 + 0.15 * k})`;
  if (s.hl) { // highlighter swipe under the headline
    const hp = easeOutCubic(clamp((u - 0.35) / 0.6));
    s.hl.style.backgroundImage = `linear-gradient(${pal[2]}, ${pal[2]})`;
    s.hl.style.backgroundSize = `${hp * 100}% 38%`;
  }
  const draw = clamp((u - 0.15) / 0.9) * exit;
  const fig = figureAt(s, t);

  // ground line
  pen([[60, GROUND], [1020, GROUND]], { w: 6, amp: 1.2 });

  if (s.prop) {
    const bob = Math.sin(t * 2.2) * 10;
    withT(770, 990 + bob, 1.35, Math.sin(t * 1.3) * 0.06, () => PROPS[s.prop](draw));
    if (s.kind === 'keyword') pen(arcPts(770, 990 + bob, 185, 170, -1.2, -1.2 + Math.PI * 2.1, 40), { w: 6, color: pal[0], p: clamp((u - 0.9) / 0.7) * exit });
    if (s.kind === 'title') for (let j = 0; j < 3; j++) { const a = -2.4 + j * 0.45; pen([[770 + Math.cos(a) * 170, 990 + Math.sin(a) * 170], [770 + Math.cos(a) * 210, 990 + Math.sin(a) * 210]], { w: 6, color: pal[0], p: clamp((u - 0.8 - j * 0.1) / 0.3) * exit }); }
  }
  if (s.num) {
    const p = s.num.isYear ? 1 : easeOutCubic(clamp(u / 1.4));
    s.big.textContent = s.num.prefix + fmt(s.num.value * p, s.num.decimals, s.num.commas);
    const coins = Math.ceil(clamp(easeOutCubic(clamp(u / 1.4))) * 8);
    for (let c = 0; c < coins; c++) ellipse(770 + Math.sin(c * 2.1) * 8, GROUND - 22 - c * 34, 92, 24, { fill: '#ffd166', w: 6, p: exit });
    if (u > 1.5) for (let j = 0; j < 4; j++) { const a = -Math.PI / 2 + (j - 1.5) * 0.5; pen([[770 + Math.cos(a) * 130, GROUND - 330 + Math.sin(a) * 60], [770 + Math.cos(a) * 165, GROUND - 330 + Math.sin(a) * 90]], { w: 6, color: pal[0], p: clamp((u - 1.5) / 0.3) * exit }); }
  }
  if (s.items) {
    const n = s.items.length, per = Math.max(0.3, (holdEnd - holdStart) / n);
    const active = clamp(Math.floor((t - holdStart) / per), -1, n - 1);
    s.items.forEach((d, j) => { d.className = j === active ? 'step on' : j < active ? 'step done' : 'step'; d.style.background = j === active ? pal[2] : 'transparent'; });
    s.pads.forEach((px, j) => {
      ellipse(px, GROUND - 4, 78, 20, { fill: j === active ? pal[0] : '#ffffff', w: 6, p: clamp((u - j * 0.12) / 0.5) * exit });
      ctx.save(); ctx.globalAlpha = exit; ctx.fillStyle = j === active ? '#ffffff' : INK; ctx.font = '900 30px sans-serif'; ctx.textAlign = 'center'; ctx.fillText(String(j + 1), px, GROUND + 7); ctx.restore();
      if (j < n - 1) { const nx = s.pads[j + 1]; pen([[px + 95, GROUND - 60], [nx - 95, GROUND - 60]], { w: 5, p: clamp((u - 0.4 - j * 0.15) / 0.5) * exit }); pen([[nx - 115, GROUND - 74], [nx - 95, GROUND - 60], [nx - 115, GROUND - 46]], { w: 5, p: clamp((u - 0.8 - j * 0.15) / 0.3) * exit }); }
    });
  }
  if (s.bars) s.bars.forEach((v, j) => {
    const grow = easeOutBack(clamp((u - 0.25 - j * 0.3) / 0.8)) * exit, x = 600 + j * 240, h = Math.max(4, 330 * v * grow);
    rect(x, GROUND - h, 150, h, { fill: j ? pal[1] : pal[0], w: 7 });
    for (let y = GROUND - h + 22; y < GROUND - 6; y += 30) pen([[x + 12, y + 14], [x + 138, y - 14]], { w: 3, color: 'rgba(255,255,255,0.55)', amp: 1 });
  });

  // the figure
  const pose = poseAt(s, t);
  if (fig.walk) { pose.walk = true; pose.face = 'smile'; }
  const facing = s.kind === 'steps' || fig.walk ? 1 : 1;
  drawFigure(fig.x, s.pads && fig.onPad >= 0 ? GROUND - 18 : GROUND, pose, 1.18, fig.lift, facing);
}

// ------------------------------------------------------------------ public API
window.setup = async (config) => {
  cfg = config;
  pal = PALETTES[hash(cfg.niche || 'x') % PALETTES.length];
  document.getElementById('pill').textContent = cfg.lang === 'en' ? (cfg.niche || '').toUpperCase() : (cfg.niche || '');
  document.getElementById('fill').style.background = pal[0];
  document.body.lang = cfg.lang === 'hi' ? 'hi' : 'en';
  ctx = document.getElementById('cv').getContext('2d');
  segs = cfg.segments.map((s, i, all) => buildSegment(s, i, all));
  await document.fonts.ready;
};

window.renderFrame = (t) => {
  T = t; strokeId = 0;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = PAPER; ctx.fillRect(0, 0, W, H);
  // faint paper texture: a few fixed specks
  ctx.fillStyle = 'rgba(0,0,0,0.035)';
  for (let i = 0; i < 140; i++) ctx.fillRect(rnd(i) * W, rnd(i + 500) * H, 2, 2);
  const cur = segs.find(s => t >= s.start && t < s.end) || segs[segs.length - 1];
  segs.forEach(s => (s.card.style.display = 'none'));
  // gentle camera push-in within each scene
  const push = cur ? clamp((t - cur.start) / (cur.end - cur.start)) : 0, z = 1 + push * 0.03;
  ctx.setTransform(z, 0, 0, z, W / 2 * (1 - z), 1050 * (1 - z));
  if (cur) updateSegment(cur, t);
  document.getElementById('fill').style.width = `${clamp(t / cfg.total) * 100}%`;
};
window.sceneReady = true;
