// Entry point: window.setup(cfg) builds the renderer; window.renderFrame(t) draws one frame of the whole video.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { SceneContent } from './sceneTypes.js';
import { MixShader, FxShader, TRANSITIONS } from './post.js';
import { clamp, hexToRgb, pendingTextures } from './util.js';

const S = { cfg: null, cache: new Map() };

async function loadFonts() {
  const F = '/node_modules/@fontsource/';
  const faces = [
    ['Inter', 'inter/files/inter-latin-500-normal.woff2', 500], ['Inter', 'inter/files/inter-latin-700-normal.woff2', 700], ['Inter', 'inter/files/inter-latin-800-normal.woff2', 800],
    ['Space Grotesk', 'space-grotesk/files/space-grotesk-latin-500-normal.woff2', 500], ['Space Grotesk', 'space-grotesk/files/space-grotesk-latin-700-normal.woff2', 700], ['Space Grotesk', 'space-grotesk/files/space-grotesk-latin-700-normal.woff2', 800],
    ['JetBrains Mono', 'jetbrains-mono/files/jetbrains-mono-latin-700-normal.woff2', 700], ['JetBrains Mono', 'jetbrains-mono/files/jetbrains-mono-latin-800-normal.woff2', 800], ['JetBrains Mono', 'jetbrains-mono/files/jetbrains-mono-latin-700-normal.woff2', 500],
    ['Noto Sans Devanagari', 'noto-sans-devanagari/files/noto-sans-devanagari-devanagari-500-normal.woff2', 500], ['Noto Sans Devanagari', 'noto-sans-devanagari/files/noto-sans-devanagari-devanagari-700-normal.woff2', 700], ['Noto Sans Devanagari', 'noto-sans-devanagari/files/noto-sans-devanagari-devanagari-800-normal.woff2', 800],
  ];
  await Promise.all(faces.map(async ([fam, f, w]) => { const ff = new FontFace(fam, `url(${F}${f})`, { weight: String(w) }); await ff.load(); document.fonts.add(ff); }));
  // latin glyphs inside Hindi text (numbers, acronyms) also need the Devanagari family's own latin range: system Noto/sans is the fallback
}

function bisect(arr, t) { let lo = 0, hi = arr.length - 1, r = -1; while (lo <= hi) { const m = (lo + hi) >> 1; if (arr[m] <= t) { r = m; lo = m + 1; } else hi = m - 1; } return r; }

window.setup = async cfg => {
  S.cfg = cfg;
  const W = cfg.width, H = cfg.height, pp = cfg.manifest.renderSettings.postProcessing || {};
  await loadFonts();
  const canvas = document.getElementById('gl');
  const r = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
  r.setPixelRatio(1); r.setSize(W, H, false);
  r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = cfg.manifest.renderSettings.exposure || 1.05;
  r.outputColorSpace = THREE.SRGBColorSpace; r.shadowMap.enabled = false;
  S.r = r;
  // the 3D world is rendered at renderScale of the output size (software WebGL is slow) and upsampled; the text overlay and
  // the captions stay at full resolution, so type is always crisp
  const sc = cfg.renderScale || 1, w3 = Math.round(W * sc), h3 = Math.round(H * sc);
  const mk = () => new THREE.WebGLRenderTarget(w3, h3, { type: THREE.HalfFloatType, samples: cfg.msaa ?? 4 });
  S.rtA = mk(); S.rtB = mk();
  const comp = new EffectComposer(r); comp.setPixelRatio(sc); comp.setSize(W, H);
  S.mix = new ShaderPass(MixShader); comp.addPass(S.mix);
  const bl = pp.bloom || {};
  if (pp.enabled !== false && bl.enabled !== false) { S.bloom = new UnrealBloomPass(new THREE.Vector2(w3, h3), bl.strength ?? 0.55, bl.radius ?? 0.45, bl.threshold ?? 0.78); comp.addPass(S.bloom); }
  comp.addPass(new OutputPass());
  S.fx = new ShaderPass(FxShader); comp.addPass(S.fx);
  S.comp = comp;
  const fx = S.fx.uniforms, on = k => pp.enabled !== false && (pp[k]?.enabled !== false);
  fx.grain.value = on('filmGrain') ? pp.filmGrain?.strength ?? 0.08 : 0; fx.vig.value = on('vignette') ? pp.vignette?.strength ?? 0.2 : 0; fx.ca.value = on('chromaticAberration') ? pp.chromaticAberration?.strength ?? 0.015 : 0;
  const look = pp.look || {}; fx.sat.value = look.saturation ?? 1; fx.gain.value = look.gain ?? 1;   // thumbnails: more saturated, brighter
  S.glitchMax = on('glitch') ? pp.glitch?.maximumStrength ?? 0.08 : 0;
  S.mix.uniforms.seed.value = (cfg.manifest.randomization?.globalSeed || 1) % 997;
  // shared scene context
  const m = cfg.manifest, pal = m.brandSystem.defaultPalette, land = W > H;
  S.g = {
    W, H, land, lang: cfg.lang, globalSeed: m.randomization?.globalSeed || 0, variation: m.randomization?.variationStrength ?? 0.5,
    palette: pal, brand: m.brandSystem, fonts: m.brandSystem.fontFamily,
    safeW: W * (1 - (m.renderSettings.safeArea.leftPercent + m.renderSettings.safeArea.rightPercent) / 100),
  };
  S.scenes = cfg.scenes;
  // transition windows between consecutive scenes (the last scene may fade out to black at the end)
  S.windows = cfg.scenes.map((sc, i) => { const d = sc.transitionOut?.durationSeconds || 0.5; return { i, d, a: sc.t1 - d * 0.7, b: sc.t1 + d * 0.3, type: Math.max(0, TRANSITIONS.indexOf(sc.transitionOut?.type || 'particle-dissolve')) + 1, dir: sc.transitionOut?.direction }; });
  // captions
  S.cap = document.getElementById('cap'); S.capLast = -1;
  const cs = m.captions || {}, base = m.brandSystem.typography.captionFontSizePixels || 54;
  Object.assign(S.cap.style, { fontSize: `${base * (land ? 1.1 : 1)}px`, bottom: `${land ? 7 : (cs.bottomOffsetPercent ?? 19)}%`, fontFamily: `"${cfg.lang === 'hi' ? 'Noto Sans Devanagari' : 'Inter'}", "Noto Sans Devanagari", sans-serif`, fontWeight: 800, display: cs.enabled === false ? 'none' : 'flex' });
  S.capHi = cs.highlightColor || '#FFCC33'; S.capDef = cs.defaultColor || '#fff';
  S.report = { textOverflow: [], frames: 0, errors: [] };
};

function getScene(i) {
  if (!S.cache.has(i)) {
    for (const k of [...S.cache.keys()]) if (k < i - 1) { S.cache.get(k).dispose(); S.cache.delete(k); }
    const sc = new SceneContent(S.scenes[i].spec, S.g);
    S.cache.set(i, sc);
    sc.textOverflow().forEach(id => S.report.textOverflow.push(`${S.scenes[i].spec.sceneId}:${id}`));
  }
  return S.cache.get(i);
}

function audioAt(t) {
  const c = S.cfg.audio, f = Math.min(c.env.length - 1, Math.max(0, Math.round(t * S.cfg.fps)));
  let beat = 0, major = 0;
  const bi = bisect(c.beats, t); if (bi >= 0) beat = Math.exp(-(t - c.beats[bi]) / 0.16);
  const mi = bisect(c.major, t); if (mi >= 0) major = Math.exp(-(t - c.major[mi]) / 0.14);
  return { env: c.env[f] || 0, beat, major };
}

function drawCaptions(t) {
  const caps = S.cfg.captions, i = bisect(caps.map(c => c.start), t);   // chunk lists are short; fine
  const c = i >= 0 && t <= caps[i].end + 0.08 ? caps[i] : null;
  if (!c) { if (S.capLast !== -2) { S.cap.innerHTML = ''; S.capLast = -2; } return; }
  if (S.capLast !== i) { S.cap.innerHTML = c.words.map(w => `<span class="w">${w.w.replace(/</g, '&lt;')}</span>`).join(''); S.capLast = i; }
  const spans = S.cap.children;
  c.words.forEach((w, k) => { const on = t >= w.start && t < w.end; spans[k].style.color = on ? S.capHi : S.capDef; spans[k].style.transform = on ? 'scale(1.06)' : 'scale(1)'; });
  const age = clamp((t - c.start) / 0.12); S.cap.style.opacity = String(age * clamp((c.end + 0.08 - t) / 0.08)); S.cap.style.transform = `translateY(${(1 - age) * 14}px)`;
}

window.renderFrame = async t => {
  const sc = S.scenes, last = sc.length - 1;
  let idx = sc.findIndex(s => t >= s.t0 && t < s.t1); if (idx < 0) idx = t < sc[0].t0 ? 0 : last;
  const audio = audioAt(t);
  const mu = S.mix.uniforms;
  // inside a transition window? (window k blends scene k into scene k+1; the final window fades to black)
  let win = null;
  for (const w of S.windows) if (t >= w.a && t <= w.b && (w.i < last || sc[w.i].transitionOut)) { win = w; break; }
  getScene(idx); if (win) getScene(win.i < last ? win.i + 1 : win.i);   // build the scene(s) now, so any texture they start loading (e.g. a thumbnail
  if (pendingTextures.length) await Promise.all(pendingTextures.splice(0, pendingTextures.length));   // body's real photo) is ready before this frame is captured
  const drawn = [];
  const draw = (i, rt) => { drawn.push(i); const s = getScene(i), d = S.scenes[i].t1 - S.scenes[i].t0; s.frame(t - S.scenes[i].t0, d, audio); S.r.setRenderTarget(rt); S.r.render(s.scene, s.camera); };
  if (win) {
    draw(win.i, S.rtA);
    if (win.i < last) draw(win.i + 1, S.rtB); else { S.r.setRenderTarget(S.rtB); S.r.setClearColor(0x000000, 1); S.r.clear(); }
    mu.type.value = win.type; mu.p.value = clamp((t - win.a) / win.d);
    mu.dir.value = win.dir === 'left' ? [-1, 0] : win.dir === 'up' ? [0, 1] : win.dir === 'down' ? [0, -1] : [1, 0];
  } else {
    draw(idx, S.rtA); mu.type.value = 0; mu.p.value = 0;
  }
  S.r.setRenderTarget(null);
  mu.tA.value = S.rtA.texture; mu.tB.value = S.rtB.texture; mu.aspect.value = S.g.W / S.g.H;
  S.fx.uniforms.time.value = t; S.fx.uniforms.seed.value = mu.seed.value;
  S.fx.uniforms.glitch.value = S.glitchMax * Math.pow(clamp(audio.major * 1.2), 3);
  S.comp.render();
  S.r.autoClear = false;
  for (const i of drawn) { const s = getScene(i); S.r.render(s.overlay, s.ocam); }
  S.r.autoClear = true;
  drawCaptions(t);
  S.report.frames++;
  return true;
};
window.getReport = () => S.report;

window.sceneReady = true;   // the module has loaded: the caller can now run setup(cfg)
window.__S = S;
