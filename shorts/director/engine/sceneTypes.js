// A scene = environment + lights + object systems + scene-type specific extras (connectors, tunnels, parallax...).
import * as THREE from 'three';
import { mulberry32, clamp, lerp, smooth, easeOutCubic, wrap, fract } from './util.js';
import { buildEnvironment, bgColor, softSprite } from './environment.js';
import { ObjectSystem } from './objects.js';
import { TextElement } from './text.js';
import { Sticker } from './stickers.js';

export const SCENE_TYPES = ['kinetic-typography', 'particle-world', 'geometry-swarm', 'data-tunnel', 'procedural-grid', 'object-assembly', 'diagram-3d', 'image-parallax', 'timeline-3d', 'wave-field', 'network-nodes', 'finale'];
const LIGHT_GAIN = 38;

function lineSegs(maxPairs, color, opacity) {
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(maxPairs * 6), 3));
  const m = new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color, transparent: true, opacity, depthWrite: false, blending: THREE.AdditiveBlending }));
  m.frustumCulled = false; return m;
}
function shock(scene3d, color, ctx) {
  const m = new THREE.Mesh(new THREE.RingGeometry(0.96, 1, 96), new THREE.MeshBasicMaterial({ color: new THREE.Color(color).multiplyScalar(2), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide }));
  m.visible = false; scene3d.add(m);
  return (age, life = 1.1) => { m.visible = age >= 0 && age < life; if (!m.visible) return; const p = age / life; m.scale.setScalar(ctx.R * (0.3 + 1.5 * (1 - Math.pow(1 - p, 3)))); m.material.opacity = (1 - p) * 0.8; m.position.z = -3; };
}

// ---- per scene-type extras: each returns update(ls)
const EXTRAS = {
  'kinetic-typography'(c) {
    const sh = shock(c.scene, c.palette.primary, c.ctx);
    return ls => { sh(ls.t - 0.15, 0.9); sh2(ls); function sh2() {} };
  },
  'particle-world'(c) {
    const nx = 36, nz = 26, n = nx * nz, a = new Float32Array(n * 3), geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(a, 3));
    const pts = new THREE.Points(geo, new THREE.PointsMaterial({ size: 0.1, color: new THREE.Color(c.palette.primary).multiplyScalar(1.5), map: softSprite(), transparent: true, opacity: 0.85, depthWrite: false, blending: THREE.AdditiveBlending })); pts.frustumCulled = false; c.scene.add(pts);
    return ls => { let i = 0; for (let z = 0; z < nz; z++) for (let x = 0; x < nx; x++) { const X = (x - nx / 2) * 0.5 * c.ctx.unit, Z = -z * 0.8 + 2; a[i * 3] = X; a[i * 3 + 1] = -c.ctx.stageH * 0.3 + Math.sin(X * 0.8 + ls.t * 0.8) * 0.5 + Math.cos(Z * 0.6 + ls.t * 0.6) * 0.4; a[i * 3 + 2] = Z; i++; } geo.attributes.position.needsUpdate = true; };
  },
  'geometry-swarm'(c) {
    const rings = [1.8, 2.6, 3.4].map((r, i) => { const m = new THREE.Mesh(new THREE.TorusGeometry(r * c.ctx.unit, 0.012, 6, 96), new THREE.MeshBasicMaterial({ color: new THREE.Color(c.palette.secondary).multiplyScalar(1.4), transparent: true, opacity: 0.35 })); m.rotation.set(1.2 + i * 0.5, i, 0); c.scene.add(m); return m; });
    return ls => rings.forEach((m, i) => { m.rotation.z = ls.t * 0.2 * (i + 1); m.material.opacity = 0.2 + 0.25 * ls.beat; });
  },
  'data-tunnel'(c) {
    const tree = c.systems.find(s => s.group === 'task'); if (!tree) return null;
    const pairs = []; tree.base.forEach((b, i) => { if (b.level > 0) { let best = -1, bd = 1e9; tree.base.forEach((p, j) => { if (p.level === b.level - 1) { const d = Math.abs(p.x - b.x); if (d < bd) { bd = d; best = j; } } }); if (best >= 0) pairs.push([best, i]); } });
    const ls3 = lineSegs(pairs.length * 12, new THREE.Color(c.palette.primary).multiplyScalar(1.6), 0.9); c.scene.add(ls3);
    return ls => { const a = ls3.geometry.attributes.position.array; let w = 0; pairs.forEach(([p, q], k) => { const A = tree.base[p], B = tree.base[q], grow = clamp((ls.u * 3.2 - B.level * 0.5 - k * 0.04)); for (let s = 0; s < 6; s++) { const f0 = s / 6 * grow, f1 = (s + 1) / 6 * grow; const bend = (f) => Math.sin(f * Math.PI) * 0.35; a.set([lerp(A.x, B.x, f0) + bend(f0), A.y, lerp(A.z, B.z, f0), lerp(A.x, B.x, f1) + bend(f1), A.y, lerp(A.z, B.z, f1)], w); w += 6; } }); ls3.geometry.setDrawRange(0, w / 3); ls3.geometry.attributes.position.needsUpdate = true; };
  },
  'procedural-grid'(c) {
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), new THREE.ShaderMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide, uniforms: { c: { value: new THREE.Color(c.palette.secondary) }, t: { value: 0 } },
      vertexShader: 'varying vec2 vU; void main(){ vU = position.xy; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }', fragmentShader: 'varying vec2 vU; uniform vec3 c; uniform float t; void main(){ vec2 g = abs(fract(vU*0.7-0.5)-0.5)/fwidth(vU*0.7); float l = 1.-min(min(g.x,g.y),1.); gl_FragColor = vec4(c*1.5, l*0.28*smoothstep(22.,2.,length(vU))); }' })); wall.position.z = -9; c.scene.add(wall);
    // the "rejection" beat: a red slash strikes through the middle of the flow at 55% of the scene
    const slash = new THREE.Mesh(new THREE.BoxGeometry(1, 0.16 * c.ctx.unit, 0.1), new THREE.MeshBasicMaterial({ color: new THREE.Color(c.palette.danger).multiplyScalar(2.2), transparent: true })); slash.rotation.z = -0.5; slash.position.z = 1.5; c.scene.add(slash);
    const sh = shock(c.scene, c.palette.danger, c.ctx);
    return ls => { const p = clamp((ls.u - 0.55) / 0.12); slash.visible = ls.u > 0.55; slash.scale.x = c.ctx.stageW * 0.85 * easeOutCubic(p); slash.material.opacity = 0.95 - 0.2 * Math.sin(ls.t * 30) * (1 - p); sh((ls.u - 0.55) * ls.dur, 0.7); };
  },
  'object-assembly'(c) {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(2.1 * c.ctx.unit, 0.02, 6, 96), new THREE.MeshBasicMaterial({ color: new THREE.Color(c.palette.primary).multiplyScalar(1.8), transparent: true, opacity: 0.8 })); ring.rotation.x = Math.PI / 2; c.scene.add(ring);
    const sh = shock(c.scene, c.palette.primary, c.ctx);
    return ls => { ring.position.y = Math.sin(ls.u * Math.PI * 2.2) * 1.8 * c.ctx.unit; ring.material.opacity = 0.8 * (1 - smooth(0.7, 1, ls.u)); sh((ls.u - 0.55) * ls.dur, 0.9); };
  },
  'diagram-3d'(c) {
    const blk = c.systems.find(s => s.group === 'block'); if (!blk) return null;
    const cols = [c.palette.primary, c.palette.danger, c.palette.accent, c.palette.primary].map(h => new THREE.Color(h));
    const links = lineSegs(blk.n * 24, new THREE.Color(c.palette.textSecondary).multiplyScalar(1.6), 0.8); c.scene.add(links);
    const spark = new THREE.Mesh(new THREE.SphereGeometry(0.17 * c.ctx.unit, 14, 10), new THREE.MeshBasicMaterial({ color: new THREE.Color(c.palette.accent).multiplyScalar(3) })); c.scene.add(spark);
    const trail = new THREE.Points(new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(new Float32Array(24 * 3), 3)), new THREE.PointsMaterial({ size: 0.16, color: new THREE.Color(c.palette.accent).multiplyScalar(2), map: softSprite(), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending })); trail.frustumCulled = false; c.scene.add(trail);
    const at = (f) => { const n = blk.n, s = (f % 1) * n, i = Math.floor(s) % n, j = (i + 1) % n, q = s - Math.floor(s), A = blk.base[i], B = blk.base[j], e = q * q * (3 - 2 * q); return [lerp(A.x, B.x, e), lerp(A.y, B.y, e), lerp(A.z, B.z, e), i]; };
    return ls => {
      const a = links.geometry.attributes.position.array; let w = 0;
      for (let i = 0; i < blk.n; i++) { const A = blk.base[i], B = blk.base[(i + 1) % blk.n]; for (let s = 0; s < 8; s++) { const f0 = s / 8, f1 = (s + 1) / 8; a.set([lerp(A.x, B.x, f0), lerp(A.y, B.y, f0), 0, lerp(A.x, B.x, f1), lerp(A.y, B.y, f1), 0], w); w += 6; } }
      links.geometry.setDrawRange(0, w / 3); links.geometry.attributes.position.needsUpdate = true;
      const f = (ls.t * 0.32 + 0.02) % 1, p = at(f); spark.position.set(p[0], p[1], p[2] + 0.3);
      const tp = trail.geometry.attributes.position.array; for (let k = 0; k < 24; k++) { const q = at(((f - k * 0.006) % 1 + 1) % 1); tp.set([q[0], q[1], q[2] + 0.3], k * 3); } trail.geometry.attributes.position.needsUpdate = true;
      for (let i = 0; i < blk.n; i++) blk.setTint(i, cols[i % cols.length], Math.abs(p[3] % blk.n - i) < 1 ? 0.8 : 0.25);
      blk.tintDirty = true;
    };
  },
  'image-parallax'(c) {
    const layers = [];
    for (let i = 0; i < 5; i++) {
      const cv = document.createElement('canvas'); cv.width = 512; cv.height = 512; const g = cv.getContext('2d'); const r = mulberry32(c.seed + i * 31);
      g.fillStyle = 'rgba(8,14,30,0.55)'; g.fillRect(0, 0, 512, 512); g.strokeStyle = c.palette.primary; g.lineWidth = 3; g.strokeRect(6, 6, 500, 500);
      for (let y = 0; y < 14; y++) { g.fillStyle = [c.palette.primary, c.palette.secondary, c.palette.accent, c.palette.textSecondary][Math.floor(r() * 4)]; g.globalAlpha = 0.65; g.fillRect(24 + r() * 40, 30 + y * 33, 40 + r() * 330, 10); } g.globalAlpha = 1;
      const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(4.2 * c.ctx.unit, 4.2 * c.ctx.unit), new THREE.MeshBasicMaterial({ map: tex, transparent: true, opacity: 0.9, depthWrite: false, toneMapped: false })); m.position.set((i - 2) * 1.5 * c.ctx.unit, (r() - 0.5) * 2, -i * 2.2); c.scene.add(m); layers.push(m);
    }
    return ls => layers.forEach((m, i) => { m.position.x = (i - 2) * 1.5 * c.ctx.unit + Math.sin(ls.t * 0.3 + i) * 0.3; m.rotation.y = (i - 2) * -0.12; m.rotation.z = Math.sin(ls.t * 0.2 + i) * 0.03; });
  },
  'timeline-3d'(c) {
    const tl = c.systems.find(s => s.group === 'timeline'); if (!tl) return null;
    const ln = lineSegs(160, new THREE.Color(c.palette.primary).multiplyScalar(1.6), 0.9); c.scene.add(ln);
    const pts = []; for (let s = 0; s <= 80; s++) { const f = s / 80; pts.push([Math.sin(f * 3.2) * c.ctx.stageW * 0.22, Math.cos(f * 2.4) * c.ctx.stageH * 0.07, -f * 20 + 3]); }
    return ls => {
      const a = ln.geometry.attributes.position.array, upto = Math.floor(clamp(ls.u * 1.15) * 80); let w = 0;
      for (let s = 0; s < upto; s++) { a.set([...pts[s], ...pts[s + 1]], w); w += 6; } ln.geometry.setDrawRange(0, w / 3); ln.geometry.attributes.position.needsUpdate = true;
      for (let i = 0; i < tl.n; i++) { const f = tl.base[i].s01, lit = smooth(f - 0.12, f, ls.u * 1.15); tl.setTint(i, lit > 0.5 ? c.palette.accent : c.palette.primary, 0.5 * lit); tl.cur[i] = lit; }
      tl.tintDirty = true;
    };
  },
  'wave-field'(c) {
    const col = c.systems.find(s => s.group === 'column'); if (!col) return null;
    const rng = mulberry32(c.seed + 5), chosen = new Set(); while (chosen.size < Math.min(4, Math.max(1, Math.floor(col.n / 5)))) chosen.add(Math.floor(rng() * col.n));
    col.focus = (i, ls) => ({ h: chosen.has(i) ? 3.6 + (i % 3) * 0.6 : 0.22, p: smooth(0.32, 0.72, ls.u) });
    return ls => { for (let i = 0; i < col.n; i++) col.setTint(i, chosen.has(i) ? c.palette.accent : null, 0.85 * smooth(0.4, 0.75, ls.u)); col.tintDirty = true; col.mat.emissiveIntensity = 0.3 + 0.9 * smooth(0.45, 0.8, ls.u); };
  },
  'network-nodes'(c) {
    const nodes = c.systems.filter(s => s.group === 'node'), centre = c.systems.find(s => ['sphere', 'orb', 'gate'].includes(s.group));
    if (!nodes.length) return null;
    const P = c.params, all = []; nodes.forEach(s => { for (let i = 0; i < s.n; i++) all.push([s, i]); });
    if (centre && P.dormantUntil != null) { centre.dormant = [P.dormantUntil - 0.08, P.dormantUntil + 0.08]; }
    const pairs = []; all.forEach(([s, i], a) => { const A = s.base[i]; all.map(([s2, j], b) => [b, Math.hypot(A.x - s2.base[j].x, A.y - s2.base[j].y, (A.z - s2.base[j].z) * 0.5)]).filter(x => x[0] !== a).sort((x, y) => x[1] - y[1]).slice(0, 2).forEach(([b]) => { if (!pairs.find(p => (p[0] === a && p[1] === b) || (p[0] === b && p[1] === a))) pairs.push([a, b]); }); if (centre) pairs.push([a, -1]); });
    const ls3 = lineSegs(pairs.length, new THREE.Color(c.palette.primary).multiplyScalar(1.3), 0.35); c.scene.add(ls3);
    const pulse = new THREE.Points(new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(new Float32Array(pairs.length * 3), 3)), new THREE.PointsMaterial({ size: 0.2, color: new THREE.Color(c.palette.accent).multiplyScalar(2.2), map: softSprite(), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending })); pulse.frustumCulled = false; c.scene.add(pulse);
    const gate = c.systems.find(s => s.group === 'gate'), rng = mulberry32(c.seed + 9), okFlag = all.map(() => rng() > (P.reject ?? 0.3));
    const posOf = (a) => { if (a < 0) return [0, 0, 0]; const [s, i] = all[a]; return [s.pos[i * 3], s.pos[i * 3 + 1], s.pos[i * 3 + 2]]; };
    return ls => {
      const aw = centre && P.dormantUntil != null ? smooth(P.dormantUntil - 0.05, P.dormantUntil + 0.1, ls.u) : 1;
      const a = ls3.geometry.attributes.position.array, pa = pulse.geometry.attributes.position.array;
      pairs.forEach(([x, y], k) => { const A = posOf(x), B = posOf(y); a.set([...A, ...B], k * 6); const f = fract(ls.t * 0.55 + k * 0.37); pa.set([lerp(B[0], A[0], f), lerp(B[1], A[1], f), lerp(B[2], A[2], f)], k * 3); });
      ls3.geometry.attributes.position.needsUpdate = true; pulse.geometry.attributes.position.needsUpdate = true; ls3.material.opacity = 0.12 + 0.3 * aw; pulse.material.opacity = aw;
      if (gate) { // decisions: approved nodes are drawn into the gate (cyan), rejected ones are pushed away (red)
        all.forEach(([s, i], a2) => { const dec = smooth(0.35, 0.8, ls.u); s.setTint(i, okFlag[a2] ? c.palette.primary : c.palette.danger, 0.85 * dec); if (!okFlag[a2]) { s.base[i].x += 0; } s.tintDirty = true; });
        gate.flash = Math.max(0, Math.sin(ls.u * 18) * 0.5) * smooth(0.3, 0.5, ls.u);
      }
    };
  },
  'finale'(c) {
    const sh = shock(c.scene, c.palette.accent, c.ctx), sh2 = shock(c.scene, c.palette.primary, c.ctx);
    const rays = new THREE.Sprite(new THREE.SpriteMaterial({ map: softSprite(), color: new THREE.Color(c.palette.primary), transparent: true, opacity: 0.35, depthWrite: false, blending: THREE.AdditiveBlending })); rays.scale.set(14 * c.ctx.unit, 14 * c.ctx.unit, 1); rays.position.z = -6; c.scene.add(rays);
    return ls => { sh(ls.t - 0.3, 1.2); sh2(ls.t - 0.55, 1.2); rays.material.opacity = 0.2 + 0.3 * smooth(0, 0.5, ls.u) + 0.2 * ls.beat; };
  },
};

// path the follow-path behaviour uses, per scene type (s in 0..1, r = instance randoms, out = Vector3)
function pathFor(sceneType, ctx) {
  const W = ctx.stageW, H = ctx.stageH;
  switch (sceneType) {
    case 'data-tunnel': return (s, r, o) => { const a = s * 18 + r[0] * 6.28, rad = (1.1 + r[1] * 1.4) * ctx.unit; o.set(Math.cos(a) * rad, Math.sin(a) * rad, lerp(4, -30, s)); };
    case 'procedural-grid': return (s, r, o) => o.set(lerp(-W * 0.62, W * 0.62, s), (Math.floor(r[1] * 7) / 6 - 0.5) * H * 0.5 + Math.sin(s * 9 + r[0] * 6) * 0.08, -1 - r[2] * 5);
    case 'timeline-3d': return (s, r, o) => o.set(Math.sin(s * 3.2) * W * 0.22, Math.cos(s * 2.4) * H * 0.07, -s * 20 + 3);
    case 'network-nodes': return (s, r, o) => { const a = s * 6.283 + r[0] * 6, rad = (1.5 + r[1] * 2) * ctx.unit; o.set(Math.cos(a) * rad, Math.sin(a * 1.3) * rad * 0.7, Math.sin(a) * rad); };
    default: return (s, r, o) => o.set((r[0] - 0.5) * W, lerp(-H * 0.3, H * 0.3, s), -1 - r[2] * 5);
  }
}

export class SceneContent {
  constructor(spec, gctx, rt) {
    this.spec = spec; this.idx = spec.order - 1;
    const aspect = gctx.W / gctx.H, fov = spec.camera?.fov || 50;
    const ctx = { ...gctx, seed: (spec.seed | 0) + gctx.globalSeed };
    // world scale: portrait stage 6.2 x 11 units, landscape 11 x 6.2
    const tanH = Math.tan(THREE.MathUtils.degToRad(fov / 2));
    ctx.unit = gctx.land ? 1.35 : 1; ctx.stageW = gctx.land ? 11 : 6.2; ctx.stageH = gctx.land ? 6.2 : 11; ctx.unitY = ctx.stageH / 11; ctx.R = Math.min(ctx.stageW, ctx.stageH) * 0.5;
    ctx.dist = (ctx.stageW / 2) / (tanH * aspect);
    ctx.textDist = 10; ctx.pxToWorld = (2 * ctx.textDist * tanH) / gctx.H;
    ctx.pxScale = gctx.H / (2 * tanH); ctx.pointPx = 0.16;
    ctx.variation = gctx.variation;
    ctx.path = pathFor(spec.sceneType, ctx);
    this.ctx = ctx; this.palette = gctx.palette; this.seed = ctx.seed; this.params = spec.sceneParams || {};
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(fov, aspect, 0.1, 200);
    this.scene.add(this.camera);
    // text lives on its own overlay (a fixed camera, drawn after tone mapping) so it stays crisp, white and inside the safe area
    this.overlay = new THREE.Scene();
    this.ocam = new THREE.PerspectiveCamera(fov, aspect, 0.1, 100);
    const rng = mulberry32(ctx.seed);
    this.env = buildEnvironment(spec.environment?.preset, spec.environment?.backgroundMotion, ctx, rng);
    this.scene.add(this.env.group);
    const fd = spec.environment?.fogDensity ?? 0.08;
    this.scene.fog = new THREE.FogExp2(new THREE.Color(bgColor(spec.environment?.preset)), fd * 0.3);
    // lights
    this.scene.add(new THREE.AmbientLight(0xffffff, 0.55));
    const hemi = new THREE.HemisphereLight(new THREE.Color(this.palette.primary), new THREE.Color(this.palette.secondary), 0.7); this.scene.add(hemi);
    const key = new THREE.DirectionalLight(0xffffff, 2.0); key.position.set(3, 6, 8); this.scene.add(key);
    this.lights = (spec.lights || []).map(l => { const L = new THREE.PointLight(new THREE.Color(l.color || '#fff'), (l.intensity || 2) * LIGHT_GAIN, 0, 1.6); const p = l.position || { x: 0, y: 2, z: 2 }; L.position.set(p.x * ctx.unit, p.y, p.z); this.scene.add(L); return L; });
    if (!this.lights.length) { const L = new THREE.PointLight(new THREE.Color(this.palette.primary), 3 * LIGHT_GAIN, 0, 1.6); L.position.set(-2, 2, 3); this.scene.add(L); this.lights.push(L); }
    // objects
    this.systems = (spec.objects || []).map((o, i) => new ObjectSystem(o, spec.sceneType, ctx, ctx.seed * 31 + i * 7919));
    this.systems.forEach(s => this.scene.add(s.group3));
    const ex = EXTRAS[spec.sceneType] || EXTRAS['kinetic-typography'];
    this.extra = ex({ scene: this.scene, ctx, palette: this.palette, systems: this.systems, seed: ctx.seed, params: this.params }) || (() => {});
    // text, parented to the camera so it stays inside the safe area whatever the camera does
    this.texts = (spec.textElements || []).map(te => {
      const el = new TextElement(te, { ...ctx, fonts: gctx.fonts, brand: gctx.brand, palette: gctx.palette, lang: gctx.lang, W: gctx.W, safeW: gctx.safeW, land: gctx.land });
      const p = te.position || { x: 0, y: 0, z: 0 };
      el.baseZ = -ctx.textDist + (p.z || 0) * 0.25;
      el.mesh.position.set(p.x * (ctx.stageW / 6.2) * 1.0, p.y * ctx.unitY * (gctx.land ? 1.0 : 1.0), el.baseZ);
      this.overlay.add(el.mesh); if (el.pointsObj) { el.pointsObj.position.set(el.mesh.position.x, el.mesh.position.y, el.baseZ); this.overlay.add(el.pointsObj); }
      return el;
    });
    // thumbnail stickers (faces, arrows, rings, badges) on the same overlay
    const vh = 2 * ctx.textDist * tanH, view = { w: vh * aspect, h: vh };
    this.stickers = (spec.stickers || []).map(st => { const sk = new Sticker(st, { view, dist: ctx.textDist }); this.overlay.add(sk.mesh); return sk; });
    // camera focus
    const target = spec.camera?.target, sysT = this.systems.find(s => s.id === target);
    const F = new THREE.Vector3(0, 0, 0);
    if (sysT) { const b = sysT.base; F.set(b.reduce((a, q) => a + q.x, 0) / b.length, b.reduce((a, q) => a + q.y, 0) / b.length, b.reduce((a, q) => a + q.z, 0) / b.length); if (sysT.group === 'task') F.z = -6; if (sysT.group === 'timeline') F.z = -8; }
    let depth = 18; if (spec.sceneType === 'data-tunnel') depth = 24;
    const tp = pathFor(spec.sceneType === 'timeline-3d' ? 'timeline-3d' : 'data-tunnel', ctx);
    this.k = { focus: F, dist: ctx.dist, depth, unit: ctx.unit, targetAt: u => { const o = new THREE.Vector3(); tp(u, [0, 0.0, 0], o); if (spec.sceneType !== 'timeline-3d') o.set(0, 0, lerp(2, -18, u)); return o; } };
    this.pose = { pos: new THREE.Vector3(), look: new THREE.Vector3(), roll: 0 }; this.pose2 = { pos: new THREE.Vector3(), look: new THREE.Vector3(), roll: 0 };
    this.fov = fov;
  }

  frame(lt, dur, audio) {
    const spec = this.spec, u = clamp(lt / dur);
    const energy = spec.energy ?? 0.6;
    const ls = { t: Math.max(0, lt), u, dur, energy, beat: audio.beat, major: audio.major, audio: audio.env };
    this.env.update(ls.t);
    this.systems.forEach(s => s.update(ls));
    this.extra(ls);
    this.texts.forEach(t => t.update(lt, audio.beat));
    const cam = spec.camera || {};
    // long scenes keep moving: after the first half the camera glides into a second preset (the manifest may also give its own
    // camera.sequence = [{from: 0.5, preset}]); the two poses are blended over 0.7 s so there is never a jump
    const base = cam.preset || 'slow-dolly-in';
    const seq = [{ from: 0, preset: base }, ...(cam.sequence || (dur > 6.5 ? [{ from: 0.5, preset: ALT_CAMERA[base] || 'slow-dolly-in' }] : []))];
    let j = 0; for (let q = 0; q < seq.length; q++) if (u >= seq[q].from) j = q;
    const pu = q => clamp((u - seq[q].from) / (1 - seq[q].from));
    cameraPose(seq[j].preset, pu(j), ls.t, cam, this.k, this.pose);
    const sinceSwitch = (u - seq[j].from) * dur;
    if (j > 0 && sinceSwitch < 0.7) {
      const prev = cameraPose(seq[j - 1].preset, pu(j - 1), ls.t, cam, this.k, this.pose2), e = smooth(0, 0.7, sinceSwitch);
      this.pose.pos.lerpVectors(prev.pos, this.pose.pos, e); this.pose.look.lerpVectors(prev.look, this.pose.look, e);
    }
    this.camera.position.copy(this.pose.pos); this.camera.lookAt(this.pose.look);
    // camera-punch on major beats
    this.camera.fov = this.fov + audio.major * 3.2 * (cam.punch ?? 1); this.camera.updateProjectionMatrix();
    this.lights.forEach((L, i) => { L.intensity = (this.spec.lights?.[i]?.intensity ?? 3) * LIGHT_GAIN * (1 + 0.25 * audio.beat); });
    // text parallax: a slight lean against the camera motion so the typography feels part of the 3D space
    this.texts.forEach(t => { t.mesh.rotation.x = (this.pose.pos.y - this.k.focus.y) * 0.004; });
    this.scene.updateMatrixWorld(); this.overlay.updateMatrixWorld();
  }

  textOverflow() { return this.texts.filter(t => t.overflow).map(t => t.spec.id); }
  dispose() { this.texts.forEach(t => t.dispose()); (this.stickers || []).forEach(t => t.dispose()); this.systems.forEach(s => s.dispose()); this.scene.traverse(o => { if (o.geometry) o.geometry.dispose(); }); }
}
import { cameraPose, ALT_CAMERA } from './camera.js';
