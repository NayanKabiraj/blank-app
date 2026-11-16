// Camera presets: closed-form paths around the scene's focus point. u = progress through the scene (0..1).
import * as THREE from 'three';
import { clamp, lerp, easeInOutCubic, easeOutCubic, wobble } from './util.js';

export const CAMERA_PRESETS = ['static-drift', 'slow-dolly-in', 'fast-dolly-in', 'dolly-out', 'orbit-left', 'orbit-right', 'crane-up', 'crane-down', 'fly-through', 'whip-pan-left', 'whip-pan-right', 'handheld-subtle', 'follow-target', 'push-orbit', 'macro-push', 'parallax-slide'];

// the preset a long scene glides into at its midpoint
export const ALT_CAMERA = { 'static-drift': 'slow-dolly-in', 'slow-dolly-in': 'orbit-right', 'fast-dolly-in': 'orbit-left', 'dolly-out': 'crane-up', 'orbit-left': 'push-orbit', 'orbit-right': 'slow-dolly-in', 'crane-up': 'orbit-left', 'crane-down': 'dolly-out', 'fly-through': 'macro-push', 'whip-pan-left': 'slow-dolly-in', 'whip-pan-right': 'slow-dolly-in', 'handheld-subtle': 'parallax-slide', 'follow-target': 'push-orbit', 'push-orbit': 'dolly-out', 'macro-push': 'orbit-right', 'parallax-slide': 'slow-dolly-in' };

export function cameraPose(preset, u, t, spec, k, out) {
  const sp = spec.speed ?? 0.6, F = k.focus, D = k.dist, e = easeInOutCubic(u), a = sp * 1.1;
  const P = out.pos, L = out.look; L.copy(F); out.roll = 0;
  const orbit = (th, ph = 0.08, dd = 1) => P.set(F.x + Math.sin(th) * D * dd, F.y + D * dd * ph, F.z + Math.cos(th) * D * dd);
  switch (preset) {
    case 'static-drift': P.set(F.x + Math.sin(t * 0.3) * 0.28, F.y + Math.cos(t * 0.23) * 0.22, F.z + D); break;
    case 'slow-dolly-in': P.set(F.x, F.y + 0.1 * D * 0.2, F.z + D * lerp(1.22, 0.9, e)); break;
    case 'fast-dolly-in': P.set(F.x, F.y, F.z + D * lerp(1.7, 0.86, easeOutCubic(u))); break;
    case 'dolly-out': P.set(F.x, F.y, F.z + D * lerp(0.78, 1.28, e)); break;
    case 'orbit-left': orbit(lerp(0.55, -0.55, e) * a * 1.2); break;
    case 'orbit-right': orbit(lerp(-0.55, 0.55, e) * a * 1.2); break;
    case 'crane-up': P.set(F.x, F.y + D * lerp(-0.45, 0.28, e) * a, F.z + D * lerp(1.05, 0.95, e)); break;
    case 'crane-down': P.set(F.x, F.y + D * lerp(0.4, -0.18, e) * a, F.z + D * lerp(1.05, 0.95, e)); break;
    case 'fly-through': {
      const z = lerp(F.z + D * 1.5, F.z - k.depth * 0.9, u);
      P.set(F.x + Math.sin(u * 5.5) * 0.35 * k.unit, F.y + Math.cos(u * 4.1) * 0.25 * k.unit, z); L.set(P.x * 0.4, P.y * 0.4, z - D * 0.8); break; }
    case 'whip-pan-left': case 'whip-pan-right': {
      const sgn = preset.endsWith('left') ? 1 : -1, yaw = sgn * 1.0 * Math.pow(1 - easeOutCubic(clamp(u / 0.38)), 2) * a;
      P.set(F.x, F.y, F.z + D * lerp(1.1, 0.95, u)); L.set(P.x - Math.sin(yaw) * D, P.y, P.z - Math.cos(yaw) * D); break; }
    case 'handheld-subtle': P.set(F.x + wobble(t * 0.9, 1) * 0.22, F.y + wobble(t * 0.8, 2) * 0.18, F.z + D * (1 + 0.02 * wobble(t * 0.5, 3))); L.set(F.x + wobble(t, 4) * 0.08, F.y + wobble(t, 5) * 0.08, F.z); break;
    case 'follow-target': {
      const tp = k.targetAt(u), ahead = k.targetAt(Math.min(1, u + 0.1));
      P.set(tp.x + 0.5 * k.unit, tp.y + 0.7, tp.z + D * 0.75); L.copy(ahead); break; }
    case 'push-orbit': orbit(lerp(-0.1, 0.55, e) * a * 1.2, 0.08, lerp(1.15, 0.8, e)); break;
    case 'macro-push': orbit(lerp(0.1, -0.22, e), 0.04, lerp(1.0, 0.5, easeOutCubic(u))); break;
    case 'parallax-slide': { const x = lerp(-0.34, 0.34, e) * D * a * 0.55; P.set(F.x + x, F.y, F.z + D); L.set(F.x + x * 0.2, F.y, F.z); break; }
    default: P.set(F.x, F.y, F.z + D * lerp(1.2, 0.9, e));
  }
  // extra hand shake (spec.shake is a fraction of the unit size)
  const sh = (spec.shake || 0) * k.unit * 6;
  if (sh) { P.x += wobble(t * 5, 7) * sh; P.y += wobble(t * 5.5, 8) * sh; }
  return out;
}
