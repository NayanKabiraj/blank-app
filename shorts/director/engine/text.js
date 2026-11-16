// On-screen text: laid out once (auto-fit to the safe area), redrawn each frame into a canvas texture on a plane that
// is parented to the camera, so camera moves never push text out of the safe area. One animation per element.
import * as THREE from 'three';
import { clamp, lerp, easeOutCubic, easeOutBack, easeOutExpo, easeInOutCubic, mulberry32, hashStr, rgba } from './util.js';

const OVERSAMPLE = 1.5;
const seg = typeof Intl !== 'undefined' && Intl.Segmenter ? new Intl.Segmenter('en', { granularity: 'grapheme' }) : null;
const clusters = s => (seg ? Array.from(seg.segment(s), x => x.segment) : Array.from(s));
const strip = w => w.replace(/[.,!?;:"'()।]/g, '').toUpperCase();

export class TextElement {
  constructor(spec, ctx) {
    this.spec = spec;
    this.ctx = ctx;
    this.start = spec.startSeconds;
    this.dur = Math.max(0.4, spec.durationSeconds);
    this.anim = spec.animation || 'kinetic-sentence';
    this.rng = mulberry32(hashStr(spec.id || spec.text) ^ ctx.seed);
    const st = spec.style || {};
    this.weight = st.weight || 800;
    this.color = st.color || ctx.palette.textPrimary;
    this.accent = {};
    Object.entries(st.accentWords || {}).forEach(([k, v]) => { this.accent[strip(k)] = v; });
    const fam = { primary: ctx.fonts.primary, secondary: ctx.fonts.secondary, monospace: ctx.fonts.monospace, inter: ctx.fonts.primary }[st.font || 'primary'] || ctx.fonts.primary;
    this.family = `"${fam}", "Noto Sans Devanagari", "Noto Sans", sans-serif`;
    this.overflow = false;
    this.canvas = document.createElement('canvas');
    this.c2 = this.canvas.getContext('2d');
    this.layout();
    this.tex = new THREE.CanvasTexture(this.canvas);
    this.tex.colorSpace = THREE.SRGBColorSpace;
    this.tex.generateMipmaps = false;
    this.tex.minFilter = THREE.LinearFilter;
    this.mat = new THREE.MeshBasicMaterial({ map: this.tex, transparent: true, depthTest: false, depthWrite: false, toneMapped: false });
    this.mesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), this.mat);
    this.mesh.renderOrder = 20;
    this.mesh.visible = false;
    const k = ctx.pxToWorld / OVERSAMPLE;
    this.mesh.scale.set(this.canvas.width * k, this.canvas.height * k, 1);
    this.pointsObj = null;
    if (this.anim === 'particle-assemble') this.buildParticles();
  }

  font(size) { return `${this.weight} ${size}px ${this.family}`; }

  layout() {
    const { W, safeW, land, lang, brand } = this.ctx;
    let text = this.spec.text;
    if (brand.typography.uppercaseHeadlines && lang !== 'hi') text = text.toLocaleUpperCase();
    const tokens = text.split(/\s+/).filter(Boolean);
    const probe = document.createElement('canvas').getContext('2d');
    const maxW = safeW * 0.94, maxLines = brand.typography.maximumHeadlineLines;
    let size = (brand.typography.preferredHeadlineFontSizePixels || 96) * (land ? 1.15 : 1) * (this.spec.style?.scale || 1);
    const minSize = brand.typography.minimumReadableFontSizePixels || 48;
    let lines;
    for (; ; size -= 4) {
      probe.font = this.font(size);
      if (lang !== 'hi') probe.letterSpacing = `${(size * 0.01).toFixed(1)}px`;
      const sp = probe.measureText(' ').width;
      const toks = tokens.map(t => ({ t, w: t === '→' ? size * 0.9 : probe.measureText(t).width }));
      lines = []; let cur = { toks: [], w: 0 };
      for (const tk of toks) {
        const add = cur.toks.length ? sp : 0;
        if (cur.toks.length && cur.w + add + tk.w > maxW) { lines.push(cur); cur = { toks: [], w: 0 }; }
        cur.w += (cur.toks.length ? sp : 0) + tk.w; cur.toks.push(tk);
      }
      lines.push(cur);
      const widest = Math.max(...toks.map(t => t.w));
      if ((lines.length <= maxLines && widest <= maxW) || size <= minSize) {
        this.overflow = lines.length > maxLines || widest > maxW;
        this.space = sp;
        break;
      }
    }
    this.size = size;
    this.lh = size * 1.14;
    this.lines = lines;
    const pad = size * 0.55;
    const w = Math.ceil(Math.max(...lines.map(l => l.w)) + pad * 2), h = Math.ceil(lines.length * this.lh + pad * 2);
    this.canvas.width = Math.ceil(w * OVERSAMPLE); this.canvas.height = Math.ceil(h * OVERSAMPLE);
    this.cw = w; this.chh = h; this.pad = pad;
    // token positions (centre aligned per line)
    this.tokens = [];
    lines.forEach((ln, li) => {
      let x = (w - ln.w) / 2;
      ln.toks.forEach(tk => {
        const y = pad + li * this.lh + this.lh / 2;
        const tok = { text: tk.t, x, y, w: tk.w, line: li, idx: this.tokens.length, color: this.accent[strip(tk.t)] || this.color, accent: !!this.accent[strip(tk.t)] };
        this.tokens.push(tok);
        x += tk.w + this.space;
      });
    });
    // grapheme clusters with positions inside each token (for per-character animations; keeps Devanagari shaped)
    const m = this.c2;
    m.font = this.font(size);
    if (lang !== 'hi') m.letterSpacing = `${(size * 0.01).toFixed(1)}px`;
    for (const tok of this.tokens) {
      const cl = clusters(tok.text); tok.chars = []; let acc = '';
      for (const ch of cl) { tok.chars.push({ ch, x: m.measureText(acc).width }); acc += ch; }
    }
    this.nChars = this.tokens.reduce((a, t) => a + t.chars.length, 0);
    this.safeOverflowPx = Math.max(0, Math.max(...lines.map(l => l.w)) - maxW);
  }

  // ---- drawing helpers (all in layout px; the canvas is scaled by OVERSAMPLE)
  setup(alpha) {
    const c = this.c2;
    c.setTransform(1, 0, 0, 1, 0, 0);
    c.clearRect(0, 0, this.canvas.width, this.canvas.height);
    c.scale(OVERSAMPLE, OVERSAMPLE);
    c.font = this.font(this.size);
    c.textAlign = 'left'; c.textBaseline = 'middle';
    if (this.ctx.lang !== 'hi') c.letterSpacing = `${(this.size * 0.01).toFixed(1)}px`;
    c.globalAlpha = alpha;
  }
  glyph(c, text, x, y, color, accent, a = 1) {
    const s = this.size;
    c.save();
    c.globalAlpha *= a;
    if (text === '→') { this.arrow(c, x, y, s * 0.9, color); c.restore(); return; }
    // dark outline-ish shadow for contrast on any background, coloured glow for accent words
    c.shadowColor = 'rgba(0,0,0,0.7)'; c.shadowBlur = s * 0.18; c.shadowOffsetY = s * 0.04;
    c.fillStyle = color; c.fillText(text, x, y);
    if (accent) { c.shadowColor = rgba(color, 0.85); c.shadowBlur = s * 0.42; c.shadowOffsetY = 0; c.fillText(text, x, y); }
    c.restore();
  }
  arrow(c, x, y, w, color) {
    c.save(); c.strokeStyle = color; c.lineWidth = this.size * 0.09; c.lineCap = 'round'; c.lineJoin = 'round';
    c.shadowColor = 'rgba(0,0,0,0.7)'; c.shadowBlur = this.size * 0.18;
    const h = this.size * 0.22; c.beginPath(); c.moveTo(x + w * 0.08, y); c.lineTo(x + w * 0.92, y);
    c.moveTo(x + w * 0.92 - h, y - h); c.lineTo(x + w * 0.92, y); c.lineTo(x + w * 0.92 - h, y + h); c.stroke(); c.restore();
  }
  drawToken(tok, o = {}) {
    const c = this.c2, { dx = 0, dy = 0, s = 1, rot = 0, a = 1 } = o;
    if (a <= 0.002) return;
    c.save();
    c.translate(tok.x + tok.w / 2 + dx, tok.y + dy); c.rotate(rot); c.scale(s, s);
    this.glyph(c, tok.text, -tok.w / 2, 0, tok.color, tok.accent, a);
    c.restore();
  }
  drawChars(tok, fn) {
    const c = this.c2;
    tok.chars.forEach((chr, i) => {
      const o = fn(chr, i, tok); if (!o || o.a <= 0.002) return;
      const cw = (tok.chars[i + 1] ? tok.chars[i + 1].x : tok.w) - chr.x;
      c.save(); c.translate(tok.x + chr.x + cw / 2 + (o.dx || 0), tok.y + (o.dy || 0)); c.rotate(o.rot || 0); c.scale(o.s || 1, o.s || 1);
      this.glyph(c, chr.ch, -cw / 2, 0, tok.color, tok.accent, o.a);
      c.restore();
    });
  }

  buildParticles() {
    // sample the finished text into points once
    const probe = document.createElement('canvas'); const sc = 0.5;
    probe.width = Math.ceil(this.cw * sc); probe.height = Math.ceil(this.chh * sc);
    const p = probe.getContext('2d'); p.scale(sc, sc); p.font = this.font(this.size); p.textBaseline = 'middle'; p.fillStyle = '#fff';
    this.tokens.forEach(t => { if (t.text !== '→') p.fillText(t.text, t.x, t.y); });
    const d = p.getImageData(0, 0, probe.width, probe.height).data;
    const pts = [], rng = this.rng, step = Math.max(2, Math.round(Math.sqrt((probe.width * probe.height) / 2600)));
    for (let y = 0; y < probe.height; y += step) for (let x = 0; x < probe.width; x += step) {
      if (d[(y * probe.width + x) * 4 + 3] > 128) pts.push([x / sc, y / sc, rng(), rng(), rng()]);
    }
    const n = pts.length, pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
    const k = this.ctx.pxToWorld;
    this.ptData = pts.map(([x, y, r1, r2, r3]) => ({ tx: (x - this.cw / 2) * k, ty: -(y - this.chh / 2) * k, r1, r2, r3 }));
    const base = new THREE.Color(this.color);
    this.ptData.forEach((q, i) => { const cc = base.clone().lerp(new THREE.Color(this.ctx.palette.primary), q.r1 * 0.6); col.set([cc.r * 1.6, cc.g * 1.6, cc.b * 1.6], i * 3); });
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    this.pointsObj = new THREE.Points(g, new THREE.PointsMaterial({ size: k * step * 1.7, vertexColors: true, transparent: true, depthTest: false, depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true, toneMapped: false }));
    this.pointsObj.renderOrder = 19; this.pointsObj.visible = false; this.pointsObj.frustumCulled = false;
  }

  // ---- per-frame
  update(lt, beat) {
    const tl = lt - this.start;
    const vis = tl >= -0.001 && tl <= this.dur + 0.3;
    this.mesh.visible = vis;
    if (this.pointsObj) this.pointsObj.visible = vis;
    if (!vis) return;
    const out = clamp((this.dur - tl) / 0.28);       // fade-out in the last 0.28 s
    const alpha = clamp(tl / 0.06) * out;
    this.setup(alpha);
    this.mesh.scale.z = 1;
    let sx = 1, mz = 0, rotY = 0, extraA = 1;
    const T = this.tokens, p = clamp(tl / Math.min(1.2, this.dur * 0.6));
    const stag = (i, n, span = 0.6) => clamp((p - (i / Math.max(1, n)) * span) / (1 - span));
    switch (this.anim) {
      case 'word-punch':
        T.forEach((t, i) => { const q = clamp((tl - i * 0.22) / 0.32); const s = easeOutBack(q, 2.6); this.drawToken(t, { s: lerp(2.2, 1, s), a: clamp(q * 3), dy: (1 - s) * -10 }); });
        break;
      case 'kinetic-sentence':
        T.forEach((t, i) => { const q = easeOutCubic(clamp((tl - i * 0.12) / 0.5)); this.drawToken(t, { dy: (1 - q) * this.size * 0.9, a: q, s: lerp(0.8, 1, q) }); });
        sx = 1 + 0.02 * Math.sin(tl * 2);
        break;
      case 'character-scatter': {
        let k = 0;
        T.forEach(t => this.drawChars(t, (ch, i) => {
          const r = mulberry32(hashStr(t.text) + i * 977); const q = easeOutCubic(clamp((tl - (k++ / this.nChars) * 0.7) / 0.55));
          const ang = r() * 6.28, dist = (1 - q) * this.size * (2 + 3 * r());
          return { dx: Math.cos(ang) * dist, dy: Math.sin(ang) * dist, rot: (1 - q) * (r() - 0.5) * 6, a: q, s: lerp(0.5, 1, q) };
        }));
        break; }
      case 'typewriter': {
        const shown = clamp(tl / Math.min(this.dur * 0.7, 0.07 * this.nChars + 0.3)) * this.nChars; let k = 0, last = null;
        T.forEach(t => this.drawChars(t, (ch, i) => { const on = k++ < shown; if (on) last = { t, ch }; return on ? { a: 1 } : null; }));
        if (last && Math.floor(tl * 2.4) % 2 === 0 && tl < this.dur - 0.3) {
          const c = this.c2; c.save(); c.fillStyle = this.ctx.palette.accent;
          const cw = (last.t.chars[last.t.chars.indexOf(last.ch) + 1] || { x: last.t.w }).x;
          c.fillRect(last.t.x + cw + 4, last.t.y - this.size * 0.45, this.size * 0.07, this.size * 0.9); c.restore();
        }
        break; }
      case 'tracking-reveal': {
        const q = easeOutCubic(clamp(tl / Math.min(1.1, this.dur * 0.6)));
        T.forEach(t => this.drawChars(t, (ch, i) => ({ dx: (i - (t.chars.length - 1) / 2) * this.size * 0.5 * (1 - q), a: q })));
        break; }
      case 'mask-reveal': {
        const q = easeOutCubic(clamp(tl / Math.min(1.0, this.dur * 0.55)));
        T.forEach(t => this.drawToken(t, {}));
        const c = this.c2, front = q * (this.cw * 1.25) - this.cw * 0.125;
        c.save(); c.globalCompositeOperation = 'destination-in';
        const g = c.createLinearGradient(front - this.cw * 0.12, 0, front, 0); g.addColorStop(0, '#000'); g.addColorStop(1, 'rgba(0,0,0,0)');
        c.fillStyle = g; c.fillRect(0, 0, this.cw, this.chh); c.restore();
        if (q < 1) { c.save(); c.globalCompositeOperation = 'lighter'; const g2 = c.createLinearGradient(front - 30, 0, front + 30, 0); g2.addColorStop(0, 'rgba(0,0,0,0)'); g2.addColorStop(0.5, rgba(this.ctx.palette.primary, 0.9)); g2.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g2; c.fillRect(front - 30, this.pad * 0.5, 60, this.chh - this.pad); c.restore(); }
        break; }
      case 'impact-zoom': {
        const q = easeOutExpo(clamp(tl / 0.45));
        sx = lerp(2.6, 1, q);
        T.forEach(t => this.drawToken(t, {}));
        const flash = Math.max(0, 1 - tl / 0.22);
        if (flash > 0) { const c = this.c2; c.save(); c.globalCompositeOperation = 'source-atop'; c.fillStyle = `rgba(255,255,255,${flash * 0.7})`; c.fillRect(0, 0, this.cw, this.chh); c.restore(); }
        mz = 0; extraA = clamp(tl / 0.05);
        break; }
      case 'particle-assemble': {
        const q = clamp(tl / Math.min(1.4, this.dur * 0.6)), fin = clamp((q - 0.62) / 0.38);
        T.forEach(t => this.drawToken(t, { a: easeOutCubic(fin) }));
        if (this.pointsObj) this.updateParticles(q, fin, alpha);
        break; }
      case 'depth-reveal': {
        const q = easeOutCubic(clamp(tl / Math.min(1.1, this.dur * 0.6)));
        mz = (1 - q) * -7; rotY = (1 - q) * 0.5; extraA = q;
        T.forEach(t => this.drawToken(t, {}));
        break; }
      case 'word-stack':
        T.forEach((t, i) => { const q = easeOutBack(clamp((tl - i * 0.28) / 0.42), 2); this.drawToken(t, { dy: (1 - q) * -this.size * 1.4, a: clamp(q * 2), s: lerp(1.3, 1, clamp(q)) }); });
        break;
      case 'slide-and-lock': {
        const q = easeOutBack(clamp(tl / 0.55), 1.2);
        T.forEach((t, i) => this.drawToken(t, { dx: (1 - q) * -this.cw * 0.9 * (1 + i * 0.12), a: clamp(q * 2) }));
        const c = this.c2, w = this.cw * 0.6 * clamp((tl - 0.35) / 0.3);
        c.save(); c.fillStyle = this.ctx.palette.primary; c.shadowColor = this.ctx.palette.primary; c.shadowBlur = 16; c.fillRect((this.cw - w) / 2, this.chh - this.pad * 0.55, w, this.size * 0.06); c.restore();
        break; }
      default: T.forEach(t => this.drawToken(t, { a: easeOutCubic(clamp(tl / 0.4)) }));
    }
    this.tex.needsUpdate = true;
    this.mat.opacity = extraA * out;
    const pulse = 1 + 0.035 * beat;
    const k = this.ctx.pxToWorld / OVERSAMPLE;
    this.mesh.scale.set(this.canvas.width * k * sx * pulse, this.canvas.height * k * sx * pulse, 1);
    this.mesh.position.z = this.baseZ + mz;
    this.mesh.rotation.y = rotY;
    if (this.pointsObj) { this.pointsObj.position.z = this.baseZ; this.pointsObj.scale.setScalar(pulse); }
  }

  updateParticles(q, fin, alpha) {
    const pos = this.pointsObj.geometry.attributes.position, a = pos.array, R = this.ctx.stageW * 0.9;
    this.ptData.forEach((d, i) => {
      const e = easeOutCubic(clamp((q - d.r1 * 0.35) / 0.65)), inv = 1 - e;
      const ang = d.r2 * 6.283 + inv * 2.2, rad = inv * R * (0.4 + d.r3);
      a[i * 3] = d.tx + Math.cos(ang) * rad; a[i * 3 + 1] = d.ty + Math.sin(ang) * rad * 0.8; a[i * 3 + 2] = inv * (d.r3 - 0.5) * 3;
    });
    pos.needsUpdate = true;
    this.pointsObj.material.opacity = alpha * (1 - fin * 0.85);
  }

  dispose() { this.tex.dispose(); this.mat.dispose(); this.mesh.geometry.dispose(); if (this.pointsObj) { this.pointsObj.geometry.dispose(); this.pointsObj.material.dispose(); } }
}
