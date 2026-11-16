// Environment presets: a gradient backdrop plus procedural decor (stars, grids, tunnels, city blocks, wave planes...).
// Every decor item is a pure function of time. `motion` is the manifest's backgroundMotion.
import * as THREE from 'three';
import { mulberry32, wrap, clamp } from './util.js';

const PRESETS = {
  'dark-tech':         { top: '#0b1830', bottom: '#04060c', glow: '#00D9FF', decor: ['dust', 'floorgrid'] },
  'neon-grid':         { top: '#1b0a3f', bottom: '#050312', glow: '#ff2bd6', decor: ['floorgrid', 'sunband', 'dust'] },
  'particle-space':    { top: '#0d1240', bottom: '#02030a', glow: '#775CFF', decor: ['stars', 'blobs'] },
  'data-network':      { top: '#0a1f3a', bottom: '#040810', glow: '#00D9FF', decor: ['netdust', 'dust'] },
  'abstract-dark':     { top: '#1a1038', bottom: '#05040c', glow: '#775CFF', decor: ['blobs', 'dust'] },
  'energy-tunnel':     { top: '#0a1a3a', bottom: '#02040a', glow: '#00D9FF', decor: ['rings', 'streaks'] },
  'minimal-light':     { top: '#2b3a66', bottom: '#0f1630', glow: '#9fc2ff', decor: ['softcone', 'dotwall'] },
  'digital-city':      { top: '#10204a', bottom: '#04060e', glow: '#FFCC33', decor: ['city', 'floorgrid'] },
  'wave-space':        { top: '#08224a', bottom: '#03060f', glow: '#00D9FF', decor: ['wavegrid', 'dust'] },
  'holographic-room':  { top: '#0a2a3a', bottom: '#030a12', glow: '#00D9FF', decor: ['holoroom', 'dust'] },
};
export const ENV_NAMES = Object.keys(PRESETS);
export const bgColor = name => (PRESETS[name] || PRESETS['abstract-dark']).bottom;

const radial = (() => { let tex; return () => { if (tex) return tex; const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d'); const r = g.createRadialGradient(64, 64, 0, 64, 64, 64); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, 128, 128); tex = new THREE.CanvasTexture(c); return tex; }; })();
export const softSprite = radial;

const pointMat = (size, color, opacity = 1) => new THREE.PointsMaterial({ size, color, map: radial(), transparent: true, opacity, depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true });

export function buildEnvironment(name, motion, ctx, rng) {
  const P = PRESETS[name] || PRESETS['abstract-dark'];
  const g = new THREE.Group(); const items = [];
  const S = ctx.unit, glow = new THREE.Color(P.glow);

  // gradient backdrop (a big inside-out sphere)
  const back = new THREE.Mesh(new THREE.SphereGeometry(90, 24, 16), new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { top: { value: new THREE.Color(P.top) }, bottom: { value: new THREE.Color(P.bottom) }, glow: { value: glow }, t: { value: 0 } },
    vertexShader: 'varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: 'varying vec3 vP; uniform vec3 top, bottom, glow; uniform float t; void main(){ float h = vP.y*0.5+0.5; vec3 c = mix(bottom, top, smoothstep(0.1,1.0,h)); float c0 = pow(max(0., 1.0 - length(vP.xy - vec2(0., 0.05))*1.35), 2.2); c += glow*c0*0.22; gl_FragColor = vec4(c,1.); }',
  }));
  back.renderOrder = -10; g.add(back);

  const fwd = { forward: 1.0, 'slow-forward': 0.45, 'fast-forward': 2.4, drift: 0.25, 'subtle-drift': 0.15, 'slow-orbit': 0.2, 'rotate-slow': 0.2, wave: 0.5, converge: 0.8 }[motion] ?? 0.4;
  const mk = {
    stars() {
      const n = 900, a = new Float32Array(n * 3);
      for (let i = 0; i < n; i++) { a[i * 3] = (rng() - 0.5) * 60 * S; a[i * 3 + 1] = (rng() - 0.5) * 60 * S; a[i * 3 + 2] = -rng() * 60; }
      const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(a, 3));
      const pts = new THREE.Points(geo, pointMat(0.16, '#cfd8ff', 0.9)); pts.frustumCulled = false; g.add(pts);
      const base = a.slice();
      items.push(t => { const p = geo.attributes.position.array; for (let i = 0; i < n; i++) p[i * 3 + 2] = wrap(base[i * 3 + 2] + t * fwd * 3, -60, 6); geo.attributes.position.needsUpdate = true; });
    },
    dust() {
      const n = 260, a = new Float32Array(n * 3), b = new Float32Array(n * 3);
      for (let i = 0; i < n; i++) { b[i * 3] = (rng() - 0.5) * 16 * S; b[i * 3 + 1] = (rng() - 0.5) * 18 * S; b[i * 3 + 2] = -rng() * 22 + 4; }
      const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(a, 3));
      const pts = new THREE.Points(geo, pointMat(0.07, glow.getStyle(), 0.7)); pts.frustumCulled = false; g.add(pts);
      items.push(t => { for (let i = 0; i < n; i++) { a[i * 3] = b[i * 3] + Math.sin(t * 0.3 + i) * 0.3; a[i * 3 + 1] = b[i * 3 + 1] + Math.cos(t * 0.25 + i * 1.7) * 0.3; a[i * 3 + 2] = wrap(b[i * 3 + 2] + t * fwd * 1.2, -18, 6); } geo.attributes.position.needsUpdate = true; });
    },
    blobs() {
      for (let i = 0; i < 5; i++) {
        const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: radial(), color: new THREE.Color(i % 2 ? P.glow : '#00D9FF'), transparent: true, opacity: 0.22, depthWrite: false, blending: THREE.AdditiveBlending }));
        const bx = (rng() - 0.5) * 8 * S, by = (rng() - 0.5) * 11 * S, bz = -6 - rng() * 12, sc = (5 + rng() * 6) * S; s.scale.set(sc, sc, 1); g.add(s);
        items.push(t => { s.position.set(bx + Math.sin(t * 0.2 * fwd * 3 + i) * 1.4, by + Math.cos(t * 0.17 + i * 2) * 1.2, bz); });
      }
    },
    floorgrid() {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(70, 70), new THREE.ShaderMaterial({
        transparent: true, depthWrite: false, fog: false, side: THREE.DoubleSide,
        uniforms: { c: { value: glow }, off: { value: 0 } },
        vertexShader: 'varying vec2 vU; void main(){ vU = position.xy; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
        fragmentShader: 'varying vec2 vU; uniform vec3 c; uniform float off; void main(){ vec2 q = vec2(vU.x, vU.y + off); vec2 gr = abs(fract(q*0.5 - 0.5) - 0.5)/fwidth(q*0.5); float l = 1.0 - min(min(gr.x, gr.y), 1.0); float fade = smoothstep(35., 3., length(vU)); gl_FragColor = vec4(c*1.4, l*fade*0.55); }',
      }));
      m.rotation.x = -Math.PI / 2; m.position.y = -3.4 * ctx.unitY; g.add(m);
      items.push(t => { m.material.uniforms.off.value = t * fwd * 2.0; });
    },
    sunband() {
      const m = new THREE.Mesh(new THREE.CircleGeometry(3.2 * S, 48), new THREE.MeshBasicMaterial({ color: new THREE.Color('#ff3bb0').multiplyScalar(1.4), transparent: true, opacity: 0.12, depthWrite: false, fog: false }));
      m.position.set(0, -2.2, -34); m.scale.setScalar(1.6); g.add(m);
    },
    rings() {
      const n = 22, ms = [];
      for (let i = 0; i < n; i++) {
        const r = new THREE.Mesh(new THREE.TorusGeometry(3.4 * S, 0.035, 6, 64), new THREE.MeshBasicMaterial({ color: (i % 3 ? glow : new THREE.Color('#775CFF')).clone().multiplyScalar(1.6), transparent: true, opacity: 0.8, fog: true }));
        g.add(r); ms.push(r);
      }
      items.push(t => ms.forEach((r, i) => { const z = wrap(-i * 2.2 + t * fwd * 5, -48, 4); r.position.z = z; r.rotation.z = i * 0.4 + t * 0.2; r.material.opacity = 0.85 * clamp(1 - Math.abs(z + 20) / 26); }));
    },
    streaks() {
      const n = 110, a = new Float32Array(n * 6), b = [];
      for (let i = 0; i < n; i++) { const ang = rng() * 6.283, rad = (1.2 + rng() * 3.4) * S; b.push([Math.cos(ang) * rad, Math.sin(ang) * rad, -rng() * 40, 1 + rng() * 3]); }
      const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(a, 3));
      const ls = new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: glow.clone().multiplyScalar(1.4), transparent: true, opacity: 0.6 })); ls.frustumCulled = false; g.add(ls);
      items.push(t => { b.forEach((q, i) => { const z = wrap(q[2] + t * fwd * 14 * q[3] * 0.4, -40, 4); a.set([q[0], q[1], z, q[0], q[1], z - 1.6 * q[3]], i * 6); }); geo.attributes.position.needsUpdate = true; });
    },
    softcone() {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: radial(), color: new THREE.Color('#9fc2ff'), transparent: true, opacity: 0.32, depthWrite: false, blending: THREE.AdditiveBlending }));
      s.scale.set(16 * S, 16 * S, 1); s.position.set(0, 1.5, -10); g.add(s);
      items.push(t => { s.position.x = Math.sin(t * 0.2) * 1.2; });
    },
    dotwall() {
      const n = 16 * 22, a = new Float32Array(n * 3);
      for (let y = 0; y < 22; y++) for (let x = 0; x < 16; x++) { const i = y * 16 + x; a[i * 3] = (x - 7.5) * 1.1 * S; a[i * 3 + 1] = (y - 10.5) * 1.1 * S; a[i * 3 + 2] = -14; }
      const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(a, 3)); g.add(new THREE.Points(geo, pointMat(0.09, '#aab8ff', 0.35)));
    },
    city() {
      const n = 70, geo = new THREE.BoxGeometry(1, 1, 1), mat = new THREE.MeshStandardMaterial({ color: '#0e1730', emissive: '#274a8a', emissiveIntensity: 0.55, roughness: 0.6, metalness: 0.4 });
      const im = new THREE.InstancedMesh(geo, mat, n); g.add(im); const d = [];
      for (let i = 0; i < n; i++) { const side = i % 2 ? 1 : -1; d.push({ x: side * (2.6 + rng() * 5) * S, z: -i * 0.7 - rng() * 2, w: 0.8 + rng() * 1.2, h: 1.5 + rng() * 7, c: rng() }); }
      const m = new THREE.Object3D(), col = new THREE.Color();
      items.push(t => d.forEach((q, i) => { const z = wrap(q.z + t * fwd * 4, -52, 4); m.position.set(q.x, -3.4 * ctx.unitY + q.h / 2, z); m.scale.set(q.w, q.h, q.w); m.updateMatrix(); im.setMatrixAt(i, m.matrix); col.set(q.c > 0.8 ? '#FFCC33' : q.c > 0.5 ? '#00D9FF' : '#7b8cff').multiplyScalar(0.35 + 0.3 * q.c); im.setColorAt(i, col); im.instanceMatrix.needsUpdate = true; im.instanceColor.needsUpdate = true; }));
    },
    wavegrid() {
      const nx = 46, nz = 34, n = nx * nz, a = new Float32Array(n * 3);
      const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(a, 3)); const pts = new THREE.Points(geo, pointMat(0.1, glow.getStyle(), 0.8)); pts.frustumCulled = false; g.add(pts);
      items.push(t => { let i = 0; for (let z = 0; z < nz; z++) for (let x = 0; x < nx; x++) { const X = (x - nx / 2) * 0.7 * S, Z = -z * 0.9; a[i * 3] = X; a[i * 3 + 1] = -3.2 * ctx.unitY + Math.sin(X * 0.7 + t * 1.6) * 0.45 + Math.cos(Z * 0.5 + t * 1.1) * 0.4; a[i * 3 + 2] = Z; i++; } geo.attributes.position.needsUpdate = true; });
    },
    holoroom() {
      const w = 7 * S, h = 12 * ctx.unitY, d = 30; const b = new THREE.BoxGeometry(w, h, d, 4, 6, 10);
      const e = new THREE.LineSegments(new THREE.WireframeGeometry(b), new THREE.LineBasicMaterial({ color: glow.clone().multiplyScalar(1.1), transparent: true, opacity: 0.16 })); e.position.z = -6; g.add(e);
      items.push(t => { e.rotation.z = Math.sin(t * 0.2) * 0.04; });
    },
    netdust() {
      const n = 46, pos = []; for (let i = 0; i < n; i++) pos.push([(rng() - 0.5) * 9 * S, (rng() - 0.5) * 12 * ctx.unitY, -3 - rng() * 14]);
      const a = new Float32Array(n * 3), la = [];
      for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) { const d = Math.hypot(pos[i][0] - pos[j][0], pos[i][1] - pos[j][1], pos[i][2] - pos[j][2]); if (d < 3.4) la.push([i, j]); }
      const ls = new Float32Array(la.length * 6), geoP = new THREE.BufferGeometry(), geoL = new THREE.BufferGeometry();
      geoP.setAttribute('position', new THREE.BufferAttribute(a, 3)); geoL.setAttribute('position', new THREE.BufferAttribute(ls, 3));
      const p1 = new THREE.Points(geoP, pointMat(0.13, glow.getStyle(), 0.9)), l1 = new THREE.LineSegments(geoL, new THREE.LineBasicMaterial({ color: glow, transparent: true, opacity: 0.18 }));
      p1.frustumCulled = l1.frustumCulled = false; g.add(p1, l1);
      items.push(t => { pos.forEach((p, i) => { a[i * 3] = p[0] + Math.sin(t * 0.3 + i) * 0.35; a[i * 3 + 1] = p[1] + Math.cos(t * 0.27 + i * 1.3) * 0.35; a[i * 3 + 2] = p[2] + Math.sin(t * 0.2 + i * 2) * 0.3; }); la.forEach(([i, j], k) => { ls.set([a[i * 3], a[i * 3 + 1], a[i * 3 + 2], a[j * 3], a[j * 3 + 1], a[j * 3 + 2]], k * 6); }); geoP.attributes.position.needsUpdate = true; geoL.attributes.position.needsUpdate = true; });
    },
  };
  P.decor.forEach(d => mk[d] && mk[d]());
  return {
    group: g, preset: name,
    update(t) {
      items.forEach(f => f(t));
      if (motion === 'rotate-slow' || motion === 'slow-orbit') g.rotation.y = t * 0.05 * (motion === 'slow-orbit' ? 1.5 : 1);
      if (motion === 'wave') g.position.y = Math.sin(t * 0.8) * 0.2;
      back.position.set(0, 0, 0);
    },
  };
}
