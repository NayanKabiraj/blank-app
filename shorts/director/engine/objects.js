// Object systems: the 3D things a scene is made of (particles, orbs, shards, rings, columns, nodes...).
// `type` picks geometry + layout, `behavior` picks the closed-form motion. Everything is a pure function of the
// scene-local time, so frames can be rendered in any order, in parallel.
import * as THREE from 'three';
import { mulberry32, clamp, lerp, easeOutCubic, easeInOutCubic, wrap, smooth } from './util.js';
import { softSprite } from './environment.js';
import { bodyMaterial, applyPhotoTexture } from './bodies.js';
import { pendingTextures } from './util.js';

export const OBJECT_TYPES = ['moon', 'earth', 'sun', 'particles', 'sphere', 'central-control-orb', 'network-node', 'decision-node', 'approval-gate', 'icosahedron', 'torus', 'tetrahedron', 'columns', 'light-bars', 'instanced-code-blocks', 'task-nodes', 'workflow-blocks', 'timeline-nodes'];
const GROUP = { particles: 'points', sphere: 'sphere', 'network-node': 'node', 'decision-node': 'node', 'central-control-orb': 'orb', 'approval-gate': 'gate', icosahedron: 'shards', torus: 'torus', tetrahedron: 'tetra', columns: 'column', 'light-bars': 'bar', 'instanced-code-blocks': 'code', 'task-nodes': 'task', 'workflow-blocks': 'block', 'timeline-nodes': 'timeline', moon: 'body', earth: 'body', sun: 'body' };

const tmpV = new THREE.Vector3(), tmpO = new THREE.Object3D(), tmpC = new THREE.Color();
const dir3 = r => { const a = r[0] * 6.2832, z = r[1] * 2 - 1, s = Math.sqrt(1 - z * z); return [Math.cos(a) * s, z, Math.sin(a) * s]; };

// ---------------------------------------------------------------- behaviours
// b = base {x,y,z,s}, r = per-instance randoms, ls = {t,u,beat,major,audio,energy}, k = {u, R, W, H}
function behave(name, b, r, i, n, ls, k, o) {
  const t = ls.t * (0.7 + 0.7 * ls.energy), u = ls.u, d = dir3(r);
  o.x = b.x; o.y = b.y; o.z = b.z; o.s = b.s; o.rx = b.rx || 0; o.ry = b.ry || 0; o.rz = b.rz || 0; o.a = 1; o.glow = 1;
  switch (name) {
    case 'float':
      o.x += Math.sin(t * 0.6 + r[0] * 6.28) * 0.2 * k.u; o.y += Math.cos(t * 0.5 + r[1] * 6.28) * 0.22 * k.u; o.z += Math.sin(t * 0.4 + r[2] * 6.28) * 0.2 * k.u;
      o.rx += t * (r[0] - 0.5) * 0.8; o.ry += t * (r[1] - 0.5) * 0.9; break;
    case 'pulse':
      o.s *= 1 + 0.09 * Math.sin(t * 7.5 + r[0] * 3) + 0.2 * ls.beat; o.glow = 1 + 0.5 * ls.beat; o.ry += t * 0.3; break;
    case 'rotate':
      o.ry += t * (0.5 + r[0]); o.rx += t * 0.3; break;
    case 'assemble': {
      const p = easeOutCubic(clamp((u * 1.9 - r[0] * 0.5) / 0.85)), far = (2.5 + 3 * r[1]) * k.u, spin = (1 - p) * 2.4, c = Math.cos(spin), s = Math.sin(spin);
      const ox = d[0] * far * (1 - p), oy = d[1] * far * (1 - p), oz = d[2] * far * (1 - p);
      o.x += ox * c - oz * s; o.y += oy; o.z += ox * s + oz * c; o.a = clamp(p * 2); o.s *= 0.25 + 0.75 * p; o.ry += (1 - p) * 4; break; }
    case 'explode': {
      const e = 1 - Math.exp(-ls.t * 2.6), life = clamp(1 - ls.t / 3.6) ;
      const sp = (1.4 + 4.6 * r[0]) * k.R * 0.55; o.x = d[0] * sp * e + b.x * 0.15; o.y = d[1] * sp * e * 1.3 + b.y * 0.15; o.z = d[2] * sp * e + b.z * 0.15;
      o.a = clamp(0.15 + life); o.s *= (0.5 + r[1]) * (0.6 + 0.4 * life); break; }
    case 'scatter':
      o.x += d[0] * (0.25 * ls.t + 1.2 * u) * k.u * (1 + r[1]); o.y += d[1] * (0.25 * ls.t + 1.2 * u) * k.u; o.z += d[2] * (0.25 * ls.t + 1.0 * u) * k.u; o.a = clamp(1.2 - u * 0.5); break;
    case 'swarm': {
      const rad = Math.hypot(b.x, b.y, b.z) || 2, ang = ls.t * (0.5 + r[0] * 0.9) + r[1] * 6.28, ax = dir3([r[2], r[0]]);
      // orbit around a tilted axis, with a breathing radius and a little flocking noise
      const px = Math.cos(ang) * rad * (1 + 0.12 * Math.sin(ls.t * 1.3 + i)), pz = Math.sin(ang) * rad * (1 + 0.12 * Math.sin(ls.t * 1.1 + i * 2));
      const py = Math.sin(ang * 1.7 + r[2] * 6) * rad * 0.35;
      const ca = Math.cos(1.2 * (r[2] - 0.5)), sa = Math.sin(1.2 * (r[2] - 0.5));
      o.x = px; o.y = py * ca - pz * sa * 0.3 + b.y * 0.2; o.z = pz * ca + py * sa * 0.3; void ax;
      o.rx += ls.t * 2 * (r[0] + 0.3); o.ry += ls.t * 1.6 * (r[1] + 0.3); break; }
    case 'spiral': {
      const a = ls.t * (0.9 + r[0] * 0.5) + i * 0.35, rad = Math.hypot(b.x, b.z) * (0.55 + 0.45 * Math.abs(Math.sin(ls.t * 0.4 + r[1]))) + 0.3 * k.u;
      o.x = Math.cos(a) * rad; o.z = Math.sin(a) * rad; o.y = b.y + Math.sin(ls.t * 0.8 + i * 0.5) * 0.4 + (u - 0.5) * 1.2 * k.u; o.ry += a; break; }
    case 'orbit': {
      const rad = Math.hypot(b.x, b.z) || 1.8 * k.u, ang = Math.atan2(b.z, b.x) + ls.t * (0.9 / (0.6 + rad * 0.25));
      o.x = Math.cos(ang) * rad; o.z = Math.sin(ang) * rad; o.rz += ls.t * 0.5 * (0.5 + r[0]); o.ry += ls.t * (0.35 + r[1] * 0.5); break; }
    case 'wave':
      o.y += Math.sin(b.x * 1.1 + ls.t * 2.4 + b.z * 0.6) * 0.45 * k.u; o.s *= 1 + 0.12 * Math.sin(ls.t * 3 + i * 0.7); break;
    case 'fall':
      o.y = wrap(b.y - ls.t * (0.9 + r[1] * 1.4) * k.u, -k.H * 0.55, k.H * 0.55); o.rz += ls.t * (r[0] - 0.5) * 2; break;
    case 'rise':
      o.y = b.y; o.sy = clamp(0.15 + 1.5 * easeOutCubic(clamp((u - r[0] * 0.3) / 0.7))) * (0.8 + 0.4 * Math.sin(ls.t * 3 + i)); break;
    case 'magnetize': {
      const p = easeInOutCubic(clamp(u * 1.35 - r[0] * 0.4)), far = (2.5 + 5 * r[1]) * k.R, sw = (1 - p) * 1.6, c = Math.cos(sw), s = Math.sin(sw);
      const fx = b.x + d[0] * far, fy = b.y + d[1] * far, fz = b.z + d[2] * far;
      const x = lerp(fx, b.x, p), y = lerp(fy, b.y, p), z = lerp(fz, b.z, p);
      o.x = x * c - y * s; o.y = x * s + y * c; o.z = z; o.a = 0.25 + 0.75 * p; o.s *= 0.6 + 0.6 * p; break; }
    case 'follow-path': {
      const s = (i / Math.max(1, n) + ls.t * 0.1 * (0.5 + ls.energy) + r[0] * 0.04) % 1;
      if (k.path) { k.path(s, r, tmpV); o.x = tmpV.x; o.y = tmpV.y; o.z = tmpV.z; } else { o.z = lerp(4, -26, s); }
      o.a = Math.sin(Math.PI * s) * 1.4 > 1 ? 1 : Math.sin(Math.PI * s) * 1.4; o.pathS = s; break; }
    case 'react-to-audio':
      o.s *= 1 + 0.9 * ls.audio; o.y += Math.sin(ls.t * 2 + i) * 0.1 * k.u; o.glow = 1 + ls.audio; break;
    default: // unknown behaviour: a gentle float
      o.y += Math.sin(t * 0.6 + r[1] * 6) * 0.15 * k.u;
  }
  return o;
}

// ---------------------------------------------------------------- layouts
function layout(group, i, n, r, k, sceneType, behavior) {
  const W = k.W, H = k.H, u = k.u;
  switch (group) {
    case 'points': {
      if (sceneType === 'finale' || behavior === 'magnetize') { const a = r[0] * 6.283, rad = Math.sqrt(r[1]) * W * 0.75; return { x: Math.cos(a) * rad, y: Math.sin(a) * rad * (H / W) * 0.9, z: -2 - r[2] * 6, s: 0.5 + r[2] }; }
      if (behavior === 'explode') return { x: 0, y: 0, z: 0, s: 0.5 + r[2] };
      const d = dir3(r), rad = (1 + r[2] * 4.5) * u; return { x: d[0] * rad * (W / 6.2), y: d[1] * rad * (H / 11) * 1.4, z: d[2] * rad - 1, s: 0.4 + r[1] };
    }
    case 'orb': case 'gate': case 'shards': case 'sphere': {
      if (n === 1) return { x: 0, y: 0, z: 0, s: 1 };
      const d = dir3(r), rad = (1.8 + r[2] * 2.4) * u; return { x: d[0] * rad, y: d[1] * rad, z: d[2] * rad, s: 0.4 + r[1] * 0.4 };
    }
    case 'node': return { x: (r[0] - 0.5) * W * 0.85, y: (r[1] - 0.5) * H * 0.55, z: -4 + r[2] * 6, s: 0.7 + r[2] * 0.7 };
    case 'torus': return { x: 0, y: 0, z: 0, s: (1.0 + i * 0.32) * u, rx: Math.PI / 2 + (i - (n - 1) / 2) * 0.38, ry: i * 0.8, rz: i * 0.5 };
    case 'tetra': { const d = dir3(r), rad = (1.7 + r[2] * 2.1) * Math.min(u, 1.3); return { x: d[0] * rad, y: d[1] * rad, z: d[2] * rad, s: 0.6 + r[1] * 0.7 }; }
    case 'column': {
      const cols = Math.max(2, Math.round(Math.sqrt(n * W / H * 1.6))), rows = Math.ceil(n / cols), c = i % cols, ro = Math.floor(i / cols), sp = W * 0.82 / cols;
      return { x: (c - (cols - 1) / 2) * sp, y: -H * 0.1, z: 0.5 - ro * sp * 1.15, s: sp * 0.7, sx: sp * 0.6, row: ro, col: c };
    }
    case 'bar': return { x: (i - (n - 1) / 2) * (W * 0.9 / n), y: -H * 0.22, z: -4, s: 1, sx: W * 0.9 / n * 0.55 };
    case 'code': return { x: (r[0] - 0.5) * W, y: (Math.floor(r[1] * 7) / 6 - 0.5) * H * 0.55, z: -1 - r[2] * 6, s: 0.5 + r[2] * 1.2, sx: 0.6 + r[0] * 1.5 };
    case 'task': {
      const lv = [1, 2, 4, 5], tot = 12; let lvl = 0, idx = i; while (idx >= lv[lvl % 4] && lvl < 3) { idx -= lv[lvl]; lvl++; }
      const cnt = lv[Math.min(lvl, 3)]; return { x: (idx - (cnt - 1) / 2) * W * 0.22 * (1 + lvl * 0.15), y: (r[1] - 0.5) * H * 0.12, z: -lvl * 4.5, s: 1, level: lvl, tot };
    }
    case 'block': { const a = Math.PI / 2 - (i / n) * 6.283, rad = Math.min(W, H) * 0.3; return { x: Math.cos(a) * rad * (W > H ? 1.2 : 1), y: Math.sin(a) * rad * (W > H ? 0.8 : 1), z: 0, s: 1 }; }
    case 'timeline': { const s = (i + 0.5) / n; return { x: Math.sin(s * 3.2) * W * 0.22, y: Math.cos(s * 2.4) * H * 0.07, z: -s * 20 + 3, s: 1, s01: s }; }
    default: { const d = dir3(r), rad = (1 + r[2] * 3) * u; return { x: d[0] * rad, y: d[1] * rad, z: d[2] * rad, s: 0.6 }; }
  }
}

// ---------------------------------------------------------------- geometry per group
function makeGeometry(group, u) {
  switch (group) {
    case 'sphere': return new THREE.SphereGeometry(0.95 * u, 40, 28);
    case 'node': return new THREE.SphereGeometry(0.16 * u, 14, 10);
    case 'orb': return new THREE.SphereGeometry(0.7 * u, 40, 28);
    case 'torus': return new THREE.TorusGeometry(1, 0.028, 8, 96);
    case 'tetra': return new THREE.TetrahedronGeometry(0.2 * u);
    case 'column': return new THREE.BoxGeometry(1, 1, 1);
    case 'bar': return new THREE.BoxGeometry(1, 1, 0.12);
    case 'code': return new THREE.BoxGeometry(0.5, 0.075 * u, 0.04);
    case 'task': return new THREE.BoxGeometry(0.55 * u, 0.36 * u, 0.1 * u);
    case 'block': return new THREE.BoxGeometry(1.05 * u, 0.72 * u, 0.3 * u);
    case 'timeline': return new THREE.SphereGeometry(0.2 * u, 20, 14);
    default: return new THREE.OctahedronGeometry(0.25 * u);   // missing-asset placeholder
  }
}

export class ObjectSystem {
  constructor(spec, sceneType, ctx, seed) {
    this.spec = spec; this.id = spec.id; this.type = spec.type; this.group3 = new THREE.Group();
    this.group = GROUP[spec.type] || 'placeholder';
    this.behavior = spec.behavior || 'float';
    this.n = Math.max(1, Math.min(spec.count || 1, 4000));
    this.audioReactive = !!spec.audioReactive;
    this.k = { u: ctx.unit, R: ctx.R, W: ctx.stageW, H: ctx.stageH, path: ctx.path };
    this.sceneType = sceneType;
    const rng = mulberry32(seed);
    this.r = Array.from({ length: this.n }, () => [rng(), rng(), rng()]);
    this.base = this.r.map((r, i) => layout(this.group, i, this.n, r, this.k, sceneType, this.behavior));
    this.cur = this.base.map(() => ({}));
    this.color = new THREE.Color(spec.color || '#00D9FF');
    this.tint = new Array(this.n).fill(null);
    this.pos = new Float32Array(this.n * 3);
    this.vis = new Float32Array(this.n).fill(1);
    const col = this.color;
    const hsl = {}; col.getHSL(hsl); this.hsl = hsl;
    const variation = ctx.variation;
    if (this.group === 'points') {
      const geo = new THREE.BufferGeometry(), a = new Float32Array(this.n * 3), c = new Float32Array(this.n * 3), s = new Float32Array(this.n);
      this.r.forEach((r, i) => { tmpC.setHSL((hsl.h + (r[1] - 0.5) * 0.08 * variation + 1) % 1, 0.8, 0.62); c.set([tmpC.r * 1.15, tmpC.g * 1.15, tmpC.b * 1.15], i * 3); s[i] = 0.5 + r[2]; });
      geo.setAttribute('position', new THREE.BufferAttribute(a, 3)); geo.setAttribute('color', new THREE.BufferAttribute(c, 3)); geo.setAttribute('size', new THREE.BufferAttribute(s, 1));
      this.mat = new THREE.ShaderMaterial({
        transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, vertexColors: true, fog: false,
        uniforms: { scale: { value: ctx.pxScale }, gain: { value: 1 }, px: { value: ctx.pointPx } },
        vertexShader: 'attribute float size; varying vec3 vC; uniform float scale, px, gain; void main(){ vC = color*gain; vec4 mv = modelViewMatrix*vec4(position,1.); gl_PointSize = clamp(size*px*scale/max(0.5,-mv.z), 1.5, 34.); gl_Position = projectionMatrix*mv; }',
        fragmentShader: 'varying vec3 vC; void main(){ float d = length(gl_PointCoord-0.5)*2.; float a = smoothstep(1.,0.,d); gl_FragColor = vec4(vC*a, a); }',
      });
      this.pts = new THREE.Points(geo, this.mat); this.pts.frustumCulled = false; this.group3.add(this.pts); this.geo = geo; this.attrAlpha = new Float32Array(this.n);
    } else if (this.group === 'shards') {
      const g0 = new THREE.IcosahedronGeometry(1.25 * ctx.unit, 1).toNonIndexed(); this.sh = { geo: g0, base: g0.attributes.position.array.slice(), faces: g0.attributes.position.count / 3 };
      this.sh.cent = Array.from({ length: this.sh.faces }, (_, f) => { const p = this.sh.base; return [0, 1, 2].map(j => (p[f * 9 + j] + p[f * 9 + 3 + j] + p[f * 9 + 6 + j]) / 3); });
      g0.computeVertexNormals();
      this.mat = new THREE.MeshStandardMaterial({ color: col, emissive: col.clone().multiplyScalar(0.55), emissiveIntensity: 1, metalness: 0.5, roughness: 0.28, flatShading: true, transparent: true });
      this.mesh = new THREE.Mesh(g0, this.mat); this.group3.add(this.mesh);
      this.edges = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.IcosahedronGeometry(1.27 * ctx.unit, 1)), new THREE.LineBasicMaterial({ color: col.clone().multiplyScalar(1.8), transparent: true, opacity: 0 })); this.group3.add(this.edges);
    } else if (this.group === 'body') {   // a textured planet: moon / earth / sun (used by thumbnails and what-if scenes)
      const R = 1.6 * ctx.unit * (spec.scale || 1), P = spec.position || {};
      this.bodyMesh = new THREE.Mesh(new THREE.SphereGeometry(R, 72, 54), bodyMaterial(spec.type, seed)); this.bodyMesh.position.set(P.x || 0, P.y || 0, P.z || 0);
      this.group3.add(this.bodyMesh);
      if (spec.photoDataUrl) pendingTextures.push(applyPhotoTexture(this.bodyMesh, spec.photoDataUrl));   // real photo, else the procedural texture above stands
      const glow = { moon: '#cfd8ff', earth: '#58a6ff', sun: '#ffb020' }[spec.type];
      this.halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: softSprite(), color: new THREE.Color(glow).multiplyScalar(spec.type === 'sun' ? 1.8 : 1.1), transparent: true, opacity: spec.type === 'sun' ? 0.9 : 0.28, depthWrite: false, blending: THREE.AdditiveBlending }));
      this.halo.scale.setScalar(R * (spec.type === 'sun' ? 6 : 3.6)); this.halo.position.copy(this.bodyMesh.position); this.halo.position.z -= 0.2; this.group3.add(this.halo);
      this.bodyR = R; this.spin = spec.spin ?? 0.12;
    } else if (this.group === 'gate') {
      this.mat = new THREE.MeshStandardMaterial({ color: col, emissive: col, emissiveIntensity: 1.1, metalness: 0.3, roughness: 0.3 });
      this.rings = [1.5, 1.1, 0.7].map((rad, j) => { const m = new THREE.Mesh(new THREE.TorusGeometry(rad * ctx.unit, 0.045 * ctx.unit, 10, 80), this.mat); this.group3.add(m); return m; });
      this.core = new THREE.Mesh(new THREE.SphereGeometry(0.34 * ctx.unit, 24, 18), new THREE.MeshBasicMaterial({ color: col.clone().multiplyScalar(2.2) })); this.group3.add(this.core);
    } else {
      const geo = makeGeometry(this.group, ctx.unit);
      this.mat = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: col.clone(), emissiveIntensity: this.group === 'column' ? 0.35 : 0.8, metalness: 0.35, roughness: 0.32 });
      this.im = new THREE.InstancedMesh(geo, this.mat, this.n); this.im.frustumCulled = false; this.group3.add(this.im);
      this.r.forEach((r, i) => { tmpC.setHSL((hsl.h + (r[1] - 0.5) * 0.06 * variation + 1) % 1, clamp(hsl.s * 0.9), clamp(hsl.l * (0.8 + 0.3 * r[0]))); this.im.setColorAt(i, tmpC); });
      this.im.instanceColor.needsUpdate = true;
      if (this.group === 'orb' || (this.group === 'sphere' && this.n === 1)) {
        this.halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: softSprite(), color: col.clone().multiplyScalar(1.4), transparent: true, opacity: 0.5, depthWrite: false, blending: THREE.AdditiveBlending }));
        this.halo.scale.setScalar(5 * ctx.unit); this.group3.add(this.halo);
      }
    }
  }

  setTint(i, color, mix) { this.tint[i] = color ? { color: new THREE.Color(color), mix } : null; }

  update(ls) {
    const o = {}, k = this.k;
    const react = this.audioReactive ? 1 : 0;
    const l2 = react ? { ...ls } : ls;
    if (this.group === 'body') { this.bodyMesh.rotation.y = 1.2 + ls.t * this.spin; this.bodyMesh.rotation.x = 0.18; return; }
    if (this.group === 'shards') return this.updateShards(ls);
    if (this.group === 'gate') return this.updateGate(ls);
    for (let i = 0; i < this.n; i++) {
      behave(this.behavior, this.base[i], this.r[i], i, this.n, ls, k, o);
      let s = o.s * (1 + react * 0.5 * ls.audio) * (1 + 0.25 * ls.major * (this.r[i][0] > 0.5 ? 1 : 0.3));
      if (this.group === 'points') {
        s *= 1 + 0.5 * ls.beat * this.r[i][2];
        this.geo.attributes.position.array.set([o.x, o.y, o.z], i * 3); this.geo.attributes.size.array[i] = Math.max(0.0001, s * o.a * (0.8 + 0.5 * this.r[i][2]));
        continue;
      }
      tmpO.position.set(o.x, o.y, o.z);
      tmpO.rotation.set(o.rx, o.ry, o.rz);
      const b = this.base[i];
      let sx = s, sy = s, sz = s;
      if (this.group === 'column') { sx = (b.sx || 1) * 0.9; sz = sx; sy = Math.max(0.05, this.colHeight(i, ls, b)); tmpO.position.y = b.y + sy / 2; }
      else if (this.group === 'bar') { sx = b.sx; sz = 1; sy = Math.max(0.05, (o.sy || 1) * this.k.H * 0.38 * (0.55 + 0.45 * this.r[i][1])); tmpO.position.y = b.y + sy / 2; }
      else if (this.group === 'code') { sx = (b.sx || 1) * o.s / (b.s || 1); sy = 1; sz = 1; }
      else if (this.group === 'torus') { sx = sy = sz = b.s * (1 + 0.04 * Math.sin(ls.t * 2 + i)); }
      tmpO.scale.set(Math.max(1e-4, sx * o.a ** 0.5), Math.max(1e-4, sy * o.a ** 0.5), Math.max(1e-4, sz * o.a ** 0.5));
      tmpO.updateMatrix(); this.im.setMatrixAt(i, tmpO.matrix);
      this.pos[i * 3] = o.x; this.pos[i * 3 + 1] = o.y; this.pos[i * 3 + 2] = o.z; this.vis[i] = o.a;
      const t = this.tint[i];
      if (t) { tmpC.setHSL(this.hsl.h, this.hsl.s, this.hsl.l).lerp(t.color, t.mix); this.im.setColorAt(i, tmpC); this.tintDirty = true; }
      this.cur[i] = o.pathS;
    }
    if (this.group === 'points') { this.geo.attributes.position.needsUpdate = true; this.geo.attributes.size.needsUpdate = true; this.mat.uniforms.gain.value = 1 + 0.5 * ls.beat + 0.5 * ls.audio * react; }
    else { this.im.instanceMatrix.needsUpdate = true; if (this.tintDirty) this.im.instanceColor.needsUpdate = true; this.mat.emissiveIntensity = (this.group === 'column' ? 0.35 : 0.8) + 0.9 * ls.beat * (react || 0.4) + 0.5 * ls.audio * react; if (this.halo) this.halo.material.opacity = 0.35 + 0.35 * ls.beat + 0.3 * this.awake(ls); }
    if (this.group === 'node' || this.group === 'orb' || this.group === 'sphere') this.applyAwake(ls);
  }

  awake(ls) { return this.dormant ? smooth(this.dormant[0], this.dormant[1], ls.u) : 1; }
  applyAwake(ls) { if (this.dormant) { const a = this.awake(ls); this.mat.emissiveIntensity = 0.12 + 1.25 * a; if (this.halo) this.halo.material.opacity = 0.08 + 0.55 * a; } }

  colHeight(i, ls, b) {
    // wave-field columns: a rolling wave; when `focus` is set most columns sink and a few chosen ones rise and glow
    const w = 0.5 + 0.5 * Math.sin(b.col * 0.9 + b.row * 0.7 + ls.t * 2.2);
    const f = this.focus ? this.focus(i, ls) : null;
    if (f === null) return 0.4 + 1.4 * w;
    return lerp(0.4 + 1.4 * w, f.h, f.p);
  }

  updateShards(ls) {
    const p = easeOutCubic(clamp(ls.u * 1.7)), { geo, base, cent, faces } = this.sh, a = geo.attributes.position.array;
    for (let f = 0; f < faces; f++) {
      const c = cent[f], rnd = ((f * 7919) % 97) / 97, q = easeOutCubic(clamp((ls.u * 1.9 - rnd * 0.6) / 0.8)), off = (1 - q) * (3 + 4 * rnd) * this.k.u;
      const len = Math.hypot(c[0], c[1], c[2]) || 1, spin = (1 - q) * (rnd - 0.5) * 6, cs = Math.cos(spin), sn = Math.sin(spin);
      for (let v = 0; v < 3; v++) {
        const j = f * 9 + v * 3, x = base[j] - c[0], y = base[j + 1] - c[1], z = base[j + 2] - c[2];
        a[j] = c[0] + x * cs - y * sn + (c[0] / len) * off; a[j + 1] = c[1] + x * sn + y * cs + (c[1] / len) * off; a[j + 2] = c[2] + z + (c[2] / len) * off;
      }
    }
    geo.attributes.position.needsUpdate = true;
    this.mesh.rotation.y = ls.t * 0.5; this.mesh.rotation.x = ls.t * 0.2; this.edges.rotation.copy(this.mesh.rotation);
    this.mesh.scale.setScalar(1 + 0.06 * ls.beat); this.edges.scale.copy(this.mesh.scale);
    this.edges.material.opacity = smooth(0.6, 0.85, ls.u) * 0.9; this.mat.opacity = 0.35 + 0.65 * p;
    this.mat.emissiveIntensity = 0.5 + 0.9 * smooth(0.5, 0.9, ls.u) + 0.8 * ls.beat;
    this.pos.set([0, 0, 0]); this.assembled = smooth(0.55, 0.9, ls.u);
  }
  updateGate(ls) {
    this.rings.forEach((m, j) => { m.rotation.x = ls.t * (0.5 + j * 0.3) * (j % 2 ? -1 : 1); m.rotation.y = ls.t * 0.4 * (j + 1) * 0.5; });
    this.group3.scale.setScalar(1 + 0.07 * ls.beat + (this.flash || 0) * 0.15);
    this.mat.emissiveIntensity = 0.9 + 1.2 * ls.beat + (this.flash || 0) * 2;
  }
  dispose() { this.group3.traverse(o => { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose && o.material.dispose(); }); }
}
