// Small deterministic helpers: seeded RNG, easing, colour. Nothing here may use Math.random() or Date.
export function mulberry32(seed) {
  let a = seed | 0;
  return function () {
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
export const easeOutCubic = x => 1 - Math.pow(1 - clamp(x), 3);
export const easeInCubic = x => Math.pow(clamp(x), 3);
export const easeInOutCubic = x => { x = clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
export const easeOutExpo = x => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * clamp(x)));
export const easeOutBack = (x, s = 1.70158) => { x = clamp(x); return 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2); };
export const fract = x => x - Math.floor(x);
export const wrap = (x, a, b) => a + ((((x - a) % (b - a)) + (b - a)) % (b - a));
// cheap smooth 1D noise from a few sines (deterministic, no state)
export const wobble = (t, s = 0) => Math.sin(t * 1.3 + s * 11.1) * 0.5 + Math.sin(t * 2.7 + s * 5.3) * 0.3 + Math.sin(t * 5.1 + s * 2.9) * 0.2;
export const hexToRgb = h => { const n = parseInt(h.replace('#', ''), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
export const rgba = (h, a) => { const [r, g, b] = hexToRgb(h); return `rgba(${r},${g},${b},${a})`; };
export const hashStr = s => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; };

// Pending async work (currently: real-photo textures for thumbnail bodies) that a frame must wait for before it is
// captured. window.renderFrame drains this after building the scene and before rendering it.
export const pendingTextures = [];
