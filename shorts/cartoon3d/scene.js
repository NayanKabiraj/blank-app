// 3D cartoon explainer scene, rendered frame by frame by render.cjs (headless Chromium).
// Everything is a pure function of time t, so renders are deterministic.
// The plan's per-scene `graphic` (title / keyword / stat / steps / compare, optional `prop`)
// decides what each scene shows. Text lives in an HTML layer so Hindi is shaped correctly.
import * as THREE from 'three';
import { OutlineEffect } from './vendor/OutlineEffect.js';

const W = 1080, H = 1920, INTRO = 0.7, OUTRO = 0.4;
const INK = '#1d1b2f';
// [sky top, sky bottom, ground, accent, accent2]
const PALETTES = [
  ['#7ec8ff', '#dff3ff', '#8fd694', '#ff7a59', '#6c5ce7'],
  ['#ffb37a', '#fff0dd', '#f7c873', '#e84393', '#0984e3'],
  ['#a29bfe', '#efeaff', '#81ecec', '#fd79a8', '#00b894'],
  ['#55efc4', '#ecfff9', '#74b9ff', '#ff7675', '#6c5ce7'],
  ['#fab1a0', '#fff3ef', '#ffeaa7', '#0984e3', '#e17055'],
  ['#74b9ff', '#eaf4ff', '#fdcb6e', '#d63031', '#00b894'],
];

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const easeOutBack = x => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const easeOutCubic = x => 1 - Math.pow(1 - x, 3);
const easeInOut = x => (x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2);
const hash = s => { let h = 7; for (const c of s) h = (h * 31 + c.charCodeAt(0)) >>> 0; return h; };

let cfg, pal, renderer, effect, scene, camera, GRAD;
let mascot, clouds = [], segs = [], propCache = {};

function gradientMap() {
  const t = new THREE.DataTexture(new Uint8Array([70, 160, 255]), 3, 1, THREE.RedFormat);
  t.minFilter = t.magFilter = THREE.NearestFilter;
  t.needsUpdate = true;
  return t;
}
const mat = (color, extra = {}) => new THREE.MeshToonMaterial({ color, gradientMap: GRAD, ...extra });
function mesh(geo, color, extra) {
  const m = new THREE.Mesh(geo, mat(color, extra));
  m.castShadow = true; m.receiveShadow = true;
  return m;
}
const group = (...kids) => { const g = new THREE.Group(); kids.forEach(k => g.add(k)); return g; };
const at = (m, x, y, z) => { m.position.set(x, y, z); return m; };

// ------------------------------------------------------------------ props (all procedural)
const PROPS = {
  star() {
    const s = new THREE.Shape();
    for (let i = 0; i < 10; i++) {
      const r = i % 2 ? 0.42 : 1.0, a = Math.PI / 2 + i * Math.PI / 5;
      i ? s.lineTo(Math.cos(a) * r, Math.sin(a) * r) : s.moveTo(Math.cos(a) * r, Math.sin(a) * r);
    }
    const g = new THREE.ExtrudeGeometry(s, { depth: 0.35, bevelEnabled: true, bevelSize: 0.08, bevelThickness: 0.08, bevelSegments: 2 });
    g.center();
    return group(mesh(g, '#fdcb6e'));
  },
  bulb() {
    return group(at(mesh(new THREE.SphereGeometry(0.75, 32, 24), '#ffeaa7', { emissive: '#fdcb6e', emissiveIntensity: 0.35 }), 0, 0.35, 0),
                 at(mesh(new THREE.CylinderGeometry(0.33, 0.28, 0.5, 24), '#b2bec3'), 0, -0.6, 0),
                 at(mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.15, 24), '#636e72'), 0, -0.92, 0));
  },
  coin() {
    const c = mesh(new THREE.CylinderGeometry(0.85, 0.85, 0.22, 40), '#f9ca24');
    const inner = at(mesh(new THREE.CylinderGeometry(0.6, 0.6, 0.24, 40), '#f0b90b'), 0, 0, 0);
    const g = group(c, inner); g.rotation.x = Math.PI / 2; return group(g);
  },
  planet() {
    const ring = mesh(new THREE.TorusGeometry(1.25, 0.09, 12, 64), pal[3]); ring.rotation.x = 1.2;
    return group(mesh(new THREE.SphereGeometry(0.8, 32, 24), pal[4]), ring);
  },
  globe() {
    const g = group(mesh(new THREE.SphereGeometry(0.9, 32, 24), '#4aa3ff'));
    [[0.5, 0.4, 0.55], [-0.4, -0.2, 0.7], [0.1, -0.6, 0.6], [-0.55, 0.45, 0.4]].forEach(([x, y, z]) =>
      g.add(at(mesh(new THREE.SphereGeometry(0.32, 16, 12), '#55c96b'), x, y, z)));
    return g;
  },
  phone() {
    return group(mesh(new THREE.BoxGeometry(1.1, 2.0, 0.2), '#2d3436'),
                 at(mesh(new THREE.BoxGeometry(0.92, 1.7, 0.04), '#a0d8ff', { emissive: '#74b9ff', emissiveIntensity: 0.4 }), 0, 0.02, 0.11));
  },
  bank() {
    const g = group(at(mesh(new THREE.BoxGeometry(2.0, 0.22, 1.1), '#dfe6e9'), 0, -0.85, 0),
                    at(mesh(new THREE.BoxGeometry(2.1, 0.22, 1.2), '#dfe6e9'), 0, 0.45, 0));
    for (const x of [-0.75, -0.25, 0.25, 0.75]) g.add(at(mesh(new THREE.CylinderGeometry(0.11, 0.11, 1.1, 16), '#ffffff'), x, -0.2, 0.2));
    const roof = at(mesh(new THREE.CylinderGeometry(0, 1.35, 0.65, 4), pal[3]), 0, 0.88, 0);
    roof.rotation.y = Math.PI / 4; roof.scale.z = 0.55; g.add(roof);
    return g;
  },
  rocket() {
    const g = group(mesh(new THREE.CylinderGeometry(0.38, 0.38, 1.4, 24), '#f5f6fa'),
                    at(mesh(new THREE.ConeGeometry(0.38, 0.6, 24), pal[3]), 0, 1.0, 0),
                    at(mesh(new THREE.CircleGeometry(0.17, 24), '#74b9ff'), 0, 0.25, 0.39));
    for (let i = 0; i < 3; i++) {
      const f = at(mesh(new THREE.BoxGeometry(0.08, 0.5, 0.45), pal[3]), 0, -0.55, 0);
      const p = group(f); f.position.z = 0.4; p.rotation.y = (i * 2 * Math.PI) / 3; g.add(p);
    }
    g.rotation.z = -0.35;
    return g;
  },
  brain() {
    const g = new THREE.Group();
    [[0, 0, 0, 0.6], [0.45, 0.15, 0, 0.45], [-0.45, 0.15, 0, 0.45], [0.25, 0.45, 0.1, 0.4], [-0.25, 0.45, 0.1, 0.4], [0.5, -0.25, 0.05, 0.38], [-0.5, -0.25, 0.05, 0.38]]
      .forEach(([x, y, z, r]) => g.add(at(mesh(new THREE.SphereGeometry(r, 20, 16), '#ff9ff3'), x, y, z)));
    return g;
  },
  chip() {
    const g = group(mesh(new THREE.BoxGeometry(1.5, 0.22, 1.5), '#2d3436'),
                    at(mesh(new THREE.BoxGeometry(0.8, 0.1, 0.8), pal[4], { emissive: pal[4], emissiveIntensity: 0.3 }), 0, 0.15, 0));
    for (let i = -2; i <= 2; i++) for (const [x, z] of [[i * 0.28, 0.85], [i * 0.28, -0.85], [0.85, i * 0.28], [-0.85, i * 0.28]])
      g.add(at(mesh(new THREE.BoxGeometry(0.1, 0.06, 0.1), '#b2bec3'), x, 0, z));
    g.rotation.x = 0.9;
    return g;
  },
  heart() {
    const g = group(at(mesh(new THREE.SphereGeometry(0.5, 24, 18), '#ff4d6d'), -0.35, 0.25, 0),
                    at(mesh(new THREE.SphereGeometry(0.5, 24, 18), '#ff4d6d'), 0.35, 0.25, 0));
    const c = at(mesh(new THREE.ConeGeometry(0.72, 1.0, 24), '#ff4d6d'), 0, -0.3, 0); c.rotation.z = Math.PI; g.add(c);
    return g;
  },
  clock() {
    const face = mesh(new THREE.CylinderGeometry(0.9, 0.9, 0.2, 40), '#ffffff'); face.rotation.x = Math.PI / 2;
    const rim = mesh(new THREE.TorusGeometry(0.9, 0.09, 12, 48), pal[3]);
    const h1 = at(mesh(new THREE.BoxGeometry(0.08, 0.5, 0.05), INK), 0, 0.22, 0.13);
    const h2 = at(mesh(new THREE.BoxGeometry(0.06, 0.7, 0.05), INK), 0, 0.3, 0.15);
    const g = group(face, rim, group(h1), group(h2));
    g.userData.spin = [g.children[2], g.children[3]];
    return g;
  },
  gear() {
    const g = group(mesh(new THREE.CylinderGeometry(0.75, 0.75, 0.35, 32), '#b2bec3'),
                    mesh(new THREE.CylinderGeometry(0.25, 0.25, 0.4, 24), '#636e72'));
    for (let i = 0; i < 10; i++) {
      const t = mesh(new THREE.BoxGeometry(0.28, 0.35, 0.3), '#b2bec3'), a = (i / 10) * Math.PI * 2;
      t.position.set(Math.cos(a) * 0.85, 0, Math.sin(a) * 0.85); t.rotation.y = -a; g.add(t);
    }
    g.rotation.x = Math.PI / 2;
    return group(g);
  },
  atom() {
    const g = group(mesh(new THREE.SphereGeometry(0.3, 24, 18), pal[3]));
    for (let i = 0; i < 3; i++) {
      const r = group(mesh(new THREE.TorusGeometry(1.0, 0.04, 8, 64), pal[4]),
                      at(mesh(new THREE.SphereGeometry(0.1, 12, 10), '#ffffff'), 1.0, 0, 0));
      r.rotation.set(i * 1.05, i * 0.6, 0); g.add(r);
    }
    g.userData.orbit = g.children.slice(1);
    return g;
  },
  book() {
    const g = group(at(mesh(new THREE.BoxGeometry(1.4, 0.3, 1.0), pal[3]), 0, -0.15, 0),
                    at(mesh(new THREE.BoxGeometry(1.32, 0.24, 0.92), '#ffffff'), 0.03, 0.08, 0),
                    at(mesh(new THREE.BoxGeometry(1.4, 0.08, 1.0), pal[4]), 0, 0.24, 0));
    g.rotation.x = 0.5;
    return g;
  },
  magnet() {
    const u = new THREE.Group();
    const arc = mesh(new THREE.TorusGeometry(0.55, 0.22, 16, 32, Math.PI), '#d63031'); arc.position.y = 0.2; u.add(arc);
    for (const x of [-0.55, 0.55]) { u.add(at(mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.6, 20), '#d63031'), x, -0.1, 0));
                                     u.add(at(mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.25, 20), '#dfe6e9'), x, -0.52, 0)); }
    return u;
  },
  cloud() {
    const g = new THREE.Group();
    [[0, 0, 0.6], [0.6, -0.1, 0.45], [-0.6, -0.1, 0.45], [0.3, 0.3, 0.45], [-0.3, 0.3, 0.42]]
      .forEach(([x, y, r]) => g.add(at(mesh(new THREE.SphereGeometry(r, 20, 16), '#ffffff'), x, y, 0)));
    return g;
  },
};
export const PROP_NAMES = Object.keys(PROPS);
const DEFAULT_PROP = { title: 'star', keyword: 'bulb', stat: 'coin' };

// ------------------------------------------------------------------ mascot
function buildMascot() {
  const body = at(mesh(new THREE.CapsuleGeometry(0.55, 0.55, 8, 20), pal[3]), 0, 1.0, 0);
  const belly = at(mesh(new THREE.SphereGeometry(0.38, 20, 16), '#ffffff'), 0, 0.85, 0.36); belly.scale.z = 0.4;
  const eyes = [], pupils = [];
  for (const x of [-0.21, 0.21]) {
    const e = at(mesh(new THREE.SphereGeometry(0.17, 20, 16), '#ffffff'), x, 1.38, 0.45);
    const p = at(new THREE.Mesh(new THREE.SphereGeometry(0.08, 16, 12), new THREE.MeshBasicMaterial({ color: INK })), 0, 0, 0.12);
    e.add(p); eyes.push(e); pupils.push(p);
  }
  const stem = at(mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.35, 8), INK), 0, 1.95, 0);
  const ball = at(mesh(new THREE.SphereGeometry(0.11, 16, 12), pal[4], { emissive: pal[4], emissiveIntensity: 0.6 }), 0, 2.15, 0);
  const arms = [];
  for (const s of [-1, 1]) {
    const arm = at(mesh(new THREE.CapsuleGeometry(0.1, 0.45, 4, 10), pal[3]), 0, -0.3, 0);
    const pivot = at(group(arm), s * 0.6, 1.15, 0); pivot.rotation.z = s * 0.35; arms.push(pivot);
  }
  const feet = [-0.25, 0.25].map(x => { const f = at(mesh(new THREE.SphereGeometry(0.2, 16, 12), INK), x, 0.15, 0.1); f.scale.set(1, 0.6, 1.4); return f; });
  const root = group(body, belly, ...eyes, stem, ball, ...arms, ...feet);
  root.userData = { eyes, pupils, arms, ball };
  root.scale.setScalar(0.85);
  return root;
}

function animateMascot(t, x, y, wave, look) {
  const m = mascot, u = m.userData;
  const bob = Math.sin(t * 3.2) * 0.05;
  m.position.set(x, y + bob, 0.9);
  m.rotation.y = 0.35 + Math.sin(t * 0.8) * 0.08;
  const squash = 1 + Math.sin(t * 6.4) * 0.02;
  m.scale.set(0.75 / Math.sqrt(squash), 0.75 * squash, 0.75 / Math.sqrt(squash));
  const blink = (t % 3.3) < 0.12 ? 0.12 : 1;
  u.eyes.forEach(e => (e.scale.y = blink));
  u.pupils.forEach(p => (p.position.x = 0.04 * look));
  u.arms[0].rotation.z = wave ? -2.1 - Math.sin(t * 14) * 0.4 : -0.35 - Math.sin(t * 2) * 0.05;
  u.arms[1].rotation.z = 0.35 + Math.sin(t * 2) * 0.05;
  u.ball.scale.setScalar(1 + Math.sin(t * 5) * 0.12);
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

// ------------------------------------------------------------------ build one segment
function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

function buildSegment(seg, i) {
  const g = seg.graphic, kind = g.kind;
  const card = el('div', 'card'); card.style.display = 'none';
  const root = new THREE.Group(); root.visible = false; scene.add(root);
  const s = { ...seg, kind, card, root, i };
  if (kind === 'stat' && parseNumber(g.headline)) {
    s.num = parseNumber(g.headline);
    s.big = el('div', 'big'); s.big.style.color = pal[3]; card.append(s.big);
    if (s.num.suffix) card.append(el('div', 'unit', s.num.suffix));
    if (g.caption) card.append(el('div', 'cap', g.caption));
    s.coins = [];
    for (let k = 0; k < 9; k++) {
      const c = PROPS.coin(); c.scale.setScalar(0.62); c.rotation.x = -Math.PI / 2; c.position.set(0.65, 0.12 + k * 0.16, 0); root.add(c); s.coins.push(c);
    }
  } else if (kind === 'steps' && g.items?.length >= 2) {
    card.append(el('div', 'head', g.headline)); card.querySelector('.head').style.fontSize = '64px';
    const list = el('div', 'steps'); s.items = g.items.slice(0, 4).map(txt => { const d = el('div', 'step', txt); list.append(d); return d; });
    card.append(list);
    const n = s.items.length;
    s.pads = s.items.map((_, k) => {
      const x = -0.95 + (k * 2.2) / (n - 1);
      const p = at(mesh(new THREE.CylinderGeometry(0.42, 0.48, 0.18, 32), '#ffffff'), x, 0.09, 0.9);
      root.add(p); return p;
    });
  } else if (kind === 'compare' && g.items?.length === 2) {
    card.append(el('div', 'head', g.headline)); card.querySelector('.head').style.fontSize = '64px';
    const row = el('div', 'cmp');
    g.items.forEach((txt, k) => { const d = el('div', null, txt); d.style.background = pal[3 + k]; d.style.color = '#fff'; row.append(d); });
    card.append(row);
    const vals = g.values?.length === 2 && Math.max(...g.values) > 0 ? g.values : [1, 1];
    const mx = Math.max(...vals);
    s.pillars = vals.map((v, k) => {
      const h = 0.3 + 1.6 * (v / mx);
      const p = mesh(new THREE.BoxGeometry(0.75, 1, 0.75), pal[3 + k]);
      p.userData.h = h; p.position.set(k ? 1.2 : 0.15, 0, 0.4); root.add(p); return p;
    });
  } else {
    card.append(el('div', 'head', g.headline));
    if (g.caption) card.append(el('div', 'cap', g.caption));
    if (kind === 'keyword') card.querySelector('.head').style.color = pal[4];
    const name = PROPS[g.prop] ? g.prop : (DEFAULT_PROP[kind] || 'star');
    const prop = PROPS[name](); prop.scale.setScalar(0.8); prop.position.set(0.55, 1.2, 0.3); root.add(prop); s.prop = prop;
    if (kind === 'keyword') {
      const ped = at(mesh(new THREE.CylinderGeometry(0.65, 0.8, 0.3, 32), '#ffffff'), 0.55, 0.15, 0.3); root.add(ped);
      const ring = mesh(new THREE.TorusGeometry(1.05, 0.05, 8, 64), pal[4]); ring.position.copy(prop.position); ring.rotation.x = 1.35; root.add(ring); s.ring = ring;
    }
  }
  document.getElementById('cards').append(card);
  return s;
}

// ------------------------------------------------------------------ per-frame update of one segment
function updateSegment(s, t) {
  const u = t - s.start, len = s.end - s.start;
  const enter = clamp(u / INTRO), exit = clamp((s.end - t) / OUTRO);
  const k = easeOutBack(enter) * easeInOut(exit);
  s.card.style.display = 'block';
  s.card.style.opacity = String(clamp(enter * 2) * exit);
  s.card.style.transform = `translateY(${(1 - enter) * 60}px) scale(${0.6 + 0.4 * k})`;
  s.root.visible = true;
  s.root.scale.setScalar(Math.max(0.001, k));
  const holdStart = s.start + INTRO, holdEnd = s.end - OUTRO;

  if (s.num) {
    const p = s.num.isYear ? 1 : easeOutCubic(clamp(u / 1.4));
    s.big.textContent = s.num.prefix + fmt(s.num.value * p, s.num.decimals, s.num.commas);
    s.coins.forEach((c, i) => { const on = clamp(p * s.coins.length - i); c.visible = on > 0; c.position.y = 0.12 + i * 0.16 + (1 - on) * 1.2; c.rotation.z = t * 0.6 + i; });
  }
  if (s.items) {
    const n = s.items.length, per = Math.max(0.3, (holdEnd - holdStart) / n);
    const active = clamp(Math.floor((t - holdStart) / per), -1, n - 1);
    s.items.forEach((d, i) => { const on = i === active; d.className = on ? 'step on' : 'step'; d.style.background = on ? pal[3] : '#f3f1ff'; });
    s.pads.forEach((p, i) => { p.material.color.set(i === active ? pal[3] : '#ffffff'); p.position.y = 0.09 + (i === active ? 0.05 + Math.sin(t * 8) * 0.02 : 0); });
  }
  if (s.pillars) s.pillars.forEach((p, i) => {
    const grow = easeOutBack(clamp((u - 0.2 - i * 0.25) / 0.8));
    const h = Math.max(0.01, p.userData.h * grow);
    p.scale.y = h; p.position.y = h / 2;
  });
  if (s.prop) {
    s.prop.rotation.y = t * 0.7;
    s.prop.position.y = 1.2 + Math.sin(t * 2.2) * 0.1;
    if (s.prop.userData.spin) s.prop.userData.spin.forEach((h, i) => (h.rotation.z = -t * (i ? 2.4 : 0.4)));
    if (s.prop.userData.orbit) s.prop.userData.orbit.forEach((r, i) => (r.rotation.z = t * (1.2 + i * 0.4)));
  }
  if (s.ring) s.ring.rotation.z = t * 0.9;
  return { holdStart, holdEnd, len };
}

// mascot path: hops onto each step pad in turn (arriving as the step lights up), else stands at home
const HOME = -1.0, HOP = 0.45, PAD_Y = 0.18;
function mascotState(s, t) {
  if (!s || !s.pads) return { x: HOME, y: 0 };
  const holdStart = s.start + INTRO, holdEnd = s.end - OUTRO, n = s.pads.length;
  const per = Math.max(0.3, (holdEnd - holdStart) / n);
  const stops = [{ t: -1e9, x: HOME, y: 0 }];
  s.pads.forEach((p, i) => stops.push({ t: holdStart + i * per, x: p.position.x, y: PAD_Y }));
  stops.push({ t: s.end, x: HOME, y: 0 });
  for (let i = 1; i < stops.length; i++) {
    const a = stops[i - 1], b = stops[i];
    if (t < b.t - HOP) return { x: a.x, y: a.y };
    if (t < b.t) {
      const p = clamp((t - (b.t - HOP)) / HOP);
      return { x: a.x + (b.x - a.x) * easeInOut(p), y: a.y + (b.y - a.y) * p + Math.sin(Math.PI * p) * 0.4 };
    }
  }
  return { x: HOME, y: 0 };
}

// ------------------------------------------------------------------ public API
window.setup = async (config) => {
  cfg = config;
  pal = PALETTES[hash(cfg.niche || 'x') % PALETTES.length];
  document.getElementById('sky').style.background = `linear-gradient(180deg, ${pal[0]} 0%, ${pal[1]} 70%)`;
  document.getElementById('pill').textContent = cfg.lang === 'en' ? (cfg.niche || '').toUpperCase() : (cfg.niche || '');
  document.body.lang = cfg.lang === 'hi' ? 'hi' : 'en';

  renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('gl'), antialias: true, alpha: true, preserveDrawingBuffer: true });
  // 3D layer at ~2/3 resolution (toon shading upscales cleanly); text stays full resolution
  renderer.setPixelRatio(cfg.glScale || 0.67); renderer.setSize(W, H, false);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  effect = new OutlineEffect(renderer, { defaultThickness: 0.0045, defaultColor: [0.11, 0.1, 0.18] });
  GRAD = gradientMap();

  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(34, W / H, 0.1, 100);
  scene.add(new THREE.HemisphereLight('#ffffff', pal[2], 1.4));
  const sun = new THREE.DirectionalLight('#ffffff', 2.2);
  sun.position.set(4, 9, 7); sun.castShadow = true; sun.shadow.mapSize.set(1024, 1024);
  Object.assign(sun.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6 }); scene.add(sun);

  const ground = at(mesh(new THREE.CylinderGeometry(7, 7, 0.5, 64), pal[2]), 0, -0.25, -1); scene.add(ground);
  for (const [x, z, r, c] of [[-4, -6, 3.2, 0.82], [3.5, -7, 3.8, 0.9], [0, -9, 4.5, 0.75]]) {
    const hill = at(mesh(new THREE.SphereGeometry(r, 32, 16), new THREE.Color(pal[2]).multiplyScalar(c)), x, -0.6, z); hill.scale.y = 0.55; scene.add(hill);
  }
  for (let i = 0; i < 4; i++) { const c = PROPS.cloud(); c.scale.setScalar(0.7 + (i % 2) * 0.3); c.userData.x0 = i * 3.3; c.userData.y = 4.1 + (i % 3) * 0.45; scene.add(c); clouds.push(c); }
  mascot = buildMascot(); scene.add(mascot);

  segs = cfg.segments.map(buildSegment);
  await document.fonts.ready;
};

window.renderFrame = (t) => {
  // camera: gentle sway plus a slow push-in within each scene
  const cur = segs.find(s => t >= s.start && t < s.end) || segs[segs.length - 1];
  const push = cur ? clamp((t - cur.start) / (cur.end - cur.start)) : 0;
  camera.position.set(Math.sin(t * 0.25) * 0.35, 2.1, 13 - push * 0.6);
  camera.lookAt(0.15, 1.2, 0);

  clouds.forEach(c => { c.position.set(((c.userData.x0 + t * 0.18) % 13) - 6.5, c.userData.y, -5); });
  segs.forEach(s => { s.card.style.display = 'none'; s.root.visible = false; });
  if (cur) updateSegment(cur, t);

  const m = mascotState(cur, t);
  const wave = cur && !cur.pads && t - cur.start < 1.4;
  animateMascot(t, m.x, m.y, wave, 1);

  document.getElementById('fill').style.width = `${clamp(t / cfg.total) * 100}%`;
  effect.render(scene, camera);
};
window.sceneReady = true;
