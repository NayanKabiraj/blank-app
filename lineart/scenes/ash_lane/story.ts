// "Ash Lane": a lamplighter with one flame and three lamps. A 9:16 line-art short built on the line-art-animation library.
// Timing comes from the narration (?cues=...), so the picture follows the voice.
import { el, pen, shape, blot, paint, limb, shoe, place, inkDefs, run, f, pt, joint, PEN, PAPER, type Vec } from '../../lib/ink.ts';
import { gait } from '../../lib/gait.ts';
import { spring, pendulum, ease, clamp, lerp, smooth, seeded } from '../../lib/motion.ts';
import { palette, applyPalette, nightTint, rgb, mix, toRGB } from '../../lib/daynight.ts';

const q = new URLSearchParams(location.search);
const num = (k: string, d: number[]) => (q.get(k) ? q.get(k)!.split(',').map(Number) : d);
const C = num('cues', [0.7, 4.2, 6.82, 10.33, 13.71, 17.13, 22.33, 24.28, 27.41]);
const D = num('durs', [3.1, 2.02, 1.71, 1.18, 2.82, 4.6, 1.45, 2.53, 4.06]);
const TOTAL = num('total', [40.5])[0];

const W = 300, H = 533, GROUND = 420, SCALE = 1.35, HEAD_Y = 285;
const LAMPS = [85, 165, 245], STAND = LAMPS.map((x) => x - 16);
const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'A lamplighter lights three street lamps' });
const { defs, filter } = inkDefs(svg, 's');
document.querySelector('#stage')!.appendChild(svg);

// --- sky + gradients
const skyG = el('linearGradient', { id: 'sky', x1: 0, y1: 0, x2: 0, y2: 1 }, defs);
const s0 = el('stop', { offset: 0 }, skyG), s1 = el('stop', { offset: 1 }, skyG);
const glow = el('radialGradient', { id: 'glow' }, defs);
el('stop', { offset: 0, 'stop-color': '#ffd27a', 'stop-opacity': 0.9 }, glow); el('stop', { offset: 0.35, 'stop-color': '#ffb347', 'stop-opacity': 0.35 }, glow); el('stop', { offset: 1, 'stop-color': '#ff9a3c', 'stop-opacity': 0 }, glow);
const moonGlow = el('radialGradient', { id: 'mg' }, defs);
el('stop', { offset: 0, 'stop-color': '#f2ecd6', 'stop-opacity': 0.55 }, moonGlow); el('stop', { offset: 1, 'stop-color': '#f2ecd6', 'stop-opacity': 0 }, moonGlow);
el('rect', { x: 0, y: 0, width: W, height: H, fill: 'url(#sky)' }, svg);

const rng = seeded(5);
const stars = Array.from({ length: 34 }, () => { const x = rng(8, 292), y = rng(10, 215); return { c: el('circle', { cx: x, cy: y, r: rng(0.5, 1.2), fill: '#efe6cf', opacity: 0 }, svg), ph: rng(0, 6.28) }; });
const moonHalo = el('circle', { cx: 232, cy: 96, r: 54, fill: 'url(#mg)', opacity: 0 }, svg);
const scene = el('g', { filter }, svg);
const moon = shape(scene, 0.9); moon.setAttribute('d', 'M232 78 A19 19 0 1 0 250 104 A15 15 0 1 1 232 78Z');

// --- hills, houses
pen(scene, 0.8).setAttribute('d', 'M0 330 Q60 296 120 322 T240 310 T300 320');
type Win = { r: SVGRectElement; k: number };
const wins: Win[] = [];
function house(x: number, w: number, h: number, roof: number, k: number): void {
  const top = GROUND - h;
  shape(scene, 1).setAttribute('d', `M${x} ${GROUND} L${x} ${top} L${x + w} ${top} L${x + w} ${GROUND}Z`);
  shape(scene, 1).setAttribute('d', `M${x - 5} ${top} L${x + w / 2} ${top - roof} L${x + w + 5} ${top}Z`);
  pen(scene, 0.6).setAttribute('d', `M${x + w / 2} ${top - roof} L${x + w / 2} ${top}`);
  const cols = w > 50 ? 2 : 1;
  for (let c = 0; c < cols; c++) for (let r = 0; r < Math.floor((h - 40) / 38) + 1; r++) {
    const wx = x + 9 + c * (w - 26) / Math.max(1, cols - 1) * (cols > 1 ? 1 : 0), wy = top + 14 + r * 38;
    if (wy + 20 > GROUND - 34) continue;
    shape(scene, 0.8).setAttribute('d', `M${wx} ${wy} h14 v20 h-14Z M${wx + 7} ${wy} v20 M${wx} ${wy + 10} h14`);
    wins.push({ r: el('rect', { x: wx, y: wy, width: 14, height: 20, fill: '#ffc864', opacity: 0 }, scene), k: k + 0.07 * wins.length });
  }
  shape(scene, 0.9).setAttribute('d', `M${x + w / 2 - 7} ${GROUND} v-24 q7 -9 14 0 v24Z`);
}
house(-8, 66, 150, 34, 0.0); house(60, 52, 120, 26, 0.1); house(118, 70, 170, 30, 0.2); house(192, 56, 132, 28, 0.15); house(252, 62, 156, 32, 0.05);

// --- ground
pen(scene, 1.1).setAttribute('d', `M0 ${GROUND} L${W} ${GROUND}`);
pen(scene, 0.7).setAttribute('d', `M0 ${GROUND + 14} L${W} ${GROUND + 14} M0 ${GROUND + 38} L${W} ${GROUND + 38} M0 ${GROUND + 74} L${W} ${GROUND + 74}`);
pen(scene, 0.55).setAttribute('d', Array.from({ length: 62 }, (_, i) => { const row = i % 3, x = (i * 37.3) % W; const y = GROUND + [0, 14, 38][row]; return `M${f(x)} ${y} l1 ${[14, 24, 36][row]}`; }).join(' '));

// --- lamps
type Lamp = { lit: number; halo: SVGCircleElement; pool: SVGEllipseElement; flame: SVGEllipseElement; glass: SVGPathElement };
const lamps: Lamp[] = LAMPS.map((x) => {
  shape(scene, 1).setAttribute('d', `M${x - 7} ${GROUND} L${x - 5} ${GROUND - 8} L${x - 2} ${HEAD_Y + 26} L${x + 2} ${HEAD_Y + 26} L${x + 5} ${GROUND - 8} L${x + 7} ${GROUND}Z`);
  pen(scene, 0.7).setAttribute('d', `M${x - 4} ${GROUND - 14} h8 M${x - 3} ${HEAD_Y + 38} h6`);
  const pool = el('ellipse', { cx: x, cy: GROUND + 6, rx: 58, ry: 9, fill: 'url(#glow)', opacity: 0 }, scene);
  const halo = el('circle', { cx: x, cy: HEAD_Y, r: 52, fill: 'url(#glow)', opacity: 0 }, scene);
  const glass = shape(scene, 1); glass.setAttribute('d', `M${x - 9} ${HEAD_Y + 12} L${x - 6} ${HEAD_Y - 9} Q${x} ${HEAD_Y - 15} ${x + 6} ${HEAD_Y - 9} L${x + 9} ${HEAD_Y + 12} Q${x} ${HEAD_Y + 17} ${x - 9} ${HEAD_Y + 12}Z`);
  shape(scene, 1).setAttribute('d', `M${x - 11} ${HEAD_Y - 9} Q${x} ${HEAD_Y - 28} ${x + 11} ${HEAD_Y - 9}Z`);
  pen(scene, 0.7).setAttribute('d', `M${x - 6} ${HEAD_Y + 12} L${x - 2} ${HEAD_Y + 26} M${x + 6} ${HEAD_Y + 12} L${x + 2} ${HEAD_Y + 26}`);
  const flame = el('ellipse', { cx: x, cy: HEAD_Y + 2, rx: 3, ry: 6, fill: '#ffb83a', opacity: 0 }, scene);
  return { lit: 0, halo, pool, flame, glass };
});
const moths = Array.from({ length: 6 }, () => el('circle', { r: 0.9, fill: '#efe6cf', opacity: 0 }, scene));

// --- Tomas
const fig = el('g', {}, scene);
const farArm = limb(fig, 3.6), legs = [limb(fig, 4.2), limb(fig, 4.2)], shoes = [blot(fig), blot(fig)];
const coat = shape(fig), coatSeam = pen(fig, PEN * 0.6);
const scarfTail = paint(fig, '#b3412d', PEN * 0.8);
const head = el('ellipse', { rx: 3.6, ry: 4.6, fill: PAPER, stroke: 'currentColor', 'stroke-width': PEN }, fig);
const hat = blot(fig);
const scarf = paint(fig, '#b3412d', PEN * 0.8);
const nearArm = limb(fig, 3.6);
const lanG = el('g', {}, fig);
const lanHalo = el('circle', { r: 20, fill: 'url(#glow)', opacity: 0.8 }, lanG);
const lanHandle = pen(lanG, PEN * 0.7);
const lanBody = paint(lanG, '#8a6a3b', PEN * 0.8);
const lanFlame = el('ellipse', { rx: 2.2, ry: 4, fill: '#ffcf5a' }, lanG);
const smoke = pen(lanG, 0.5); smoke.setAttribute('opacity', '0');
const drop = el('ellipse', { rx: 1.1, ry: 1.7, fill: '#ffcf5a', opacity: 0 }, scene);

const walk = gait({ kind: 'walk' });
const SPEED = walk.speed * SCALE;
const armSwing = [spring(60, 9), spring(60, 9)];
const lanSwing = pendulum(14, 1.8);
const tail = spring(30, 4);

// --- the timeline (everything keys off the narration cues)
const win = (t: number, a: number, b: number, c: number, d: number) => (t < b ? ease((t - a) / (b - a)) : t < c ? 1 : 1 - ease((t - c) / (d - c)));
type Seg = { ta: number; tb: number; x0: number; x1: number };
const SEGS: Seg[] = [
  { ta: 0, tb: C[2] - 0.3, x0: -30, x1: STAND[0] },
  { ta: C[2] + 1.7, tb: C[3] - 0.1, x0: STAND[0], x1: STAND[1] },
  { ta: C[3] + 1.5, tb: C[4], x0: STAND[1], x1: STAND[2] },
  { ta: C[7] + 2.4, tb: Math.max(C[7] + 5, C[8] + D[8] + 0.4), x0: STAND[2], x1: -45 },
];
function where(t: number): { x: number; v: number; dir: 1 | -1 } {
  let x = SEGS[0].x0, v = 0;
  for (const s of SEGS) {
    if (t >= s.tb) { x = s.x1; continue; }
    if (t >= s.ta) {
      const T = s.tb - s.ta, u = t - s.ta, r = Math.min(0.4, T / 3), D = s.x1 - s.x0, vm = D / (T - r);
      const p = u < r ? (u * u) / (2 * r) : u < T - r ? r / 2 + (u - r) : T - r - ((T - u) ** 2) / (2 * r);
      const vv = Math.abs(vm) * Math.min(1, u / r, (T - u) / r);
      x = s.x0 + vm * p; v = vv; break;
    }
    x = s.x0; break;
  }
  return { x, v, dir: t >= C[7] + 2.4 ? -1 : 1 };
}
let phase = 0;
const smokeAt = C[7] + 1.4;

run((t, dt) => {
  // time of day: golden hour to night over the story
  const tau = 0.72 + 0.12 * ease(clamp(t / (TOTAL * 0.85), 0, 1));
  const P = palette(tau);
  applyPalette(svg, P);
  s0.setAttribute('stop-color', rgb(P.top)); s1.setAttribute('stop-color', rgb(P.bottom));
  const night = P.night;
  stars.forEach((s) => s.c.setAttribute('opacity', f(night * (0.55 + 0.45 * Math.sin(t * 1.7 + s.ph)))));
  moonHalo.setAttribute('opacity', f(night)); moon.setAttribute('fill', rgb(mix(toRGB('#fdfcf8'), toRGB('#f2ecd6'), P.inkT)));
  wins.forEach((w) => w.r.setAttribute('opacity', f(smooth(0.1, 0.5, P.lamp * 1.4 - w.k))));

  // lamps
  const sputter = (t > C[4] + 1.2 && t < C[6] + 1.2) ? 0.2 * Math.max(0, Math.sin(t * 23) * Math.sin(t * 7.3)) : 0;
  const lit = [smooth(C[2] + 0.9, C[2] + 1.5, t), smooth(C[3] + 0.7, C[3] + 1.2, t), Math.max(sputter, smooth(C[7] + 0.2, C[7] + 1.0, t))];
  lamps.forEach((L, i) => {
    const fl = 1 + 0.04 * Math.sin(t * 9 + i * 2) + 0.03 * Math.sin(t * 17 + i);
    L.halo.setAttribute('opacity', f(lit[i] * 0.95 * fl)); L.pool.setAttribute('opacity', f(lit[i] * 0.85));
    L.flame.setAttribute('opacity', f(Math.min(1, lit[i] * 1.5))); L.flame.setAttribute('ry', f(6 * fl));
    L.glass.setAttribute('fill', lit[i] > 0.05 ? rgb(mix(toRGB('#fdfcf8'), toRGB('#ffe3a0'), lit[i])) : PAPER);
  });
  moths.forEach((m, i) => { const li = i % 3, a = t * (1.6 + i * 0.3) + i * 2; m.setAttribute('cx', f(LAMPS[li] + 15 * Math.cos(a) * Math.cos(t * 0.7 + i))); m.setAttribute('cy', f(HEAD_Y + 4 + 11 * Math.sin(a * 1.3))); m.setAttribute('opacity', f(lit[li] > 0.5 ? 0.9 : 0)); });

  // Tomas: where he is and how he stands
  const w = where(t);
  const go = w.v / SPEED;
  phase += (dt / walk.period) * go;
  const dir = w.dir;
  place(fig, w.x, GROUND, dir, SCALE);
  const p = walk.pose(phase, clamp(go, 0, 1));
  const b = p.bob;
  p.feet.forEach((fo, i) => { legs[i].draw([p.hip, fo.knee, fo.ankle], [0.3, 0.8]); shoe(shoes[i], fo.ankle, fo.pitch); });
  fig.insertBefore(legs[p.front].g, coat); fig.insertBefore(shoes[p.front], coat);

  const kF = p.feet[p.front].knee, aF = p.feet[p.front].ankle;
  const sh: Vec = [41, 41 + b], hemY = 92;
  const fx = Math.max(kF[0] + 2.4, 46.4);
  coat.setAttribute('d', `M${f(sh[0] - 6)} ${f(sh[1] + 1)} Q${f(sh[0] - 1)} ${f(sh[1] - 2.4)} ${f(sh[0] + 5)} ${f(sh[1] + 1)} L${f(fx - 0.6)} ${f(70 + b)} Q${f(fx)} ${f(82 + b * 0.5)} ${f(Math.max(fx, aF[0] - 4))} ${hemY} L${f(30.6)} ${hemY + 1} L${f(33.2)} ${f(70 + b)}Z`);
  coatSeam.setAttribute('d', `M${f(sh[0] + 2.6)} ${f(sh[1] + 4)} L${f(sh[0] + 3.8)} ${f(66 + b)}`);
  coat.setAttribute('fill', PAPER);
  const hc: Vec = [42.6, 31.6 + b];
  head.setAttribute('cx', f(hc[0])); head.setAttribute('cy', f(hc[1]));
  hat.setAttribute('d', `M${f(hc[0] - 6.4)} ${f(hc[1] - 3.6)} L${f(hc[0] + 6.6)} ${f(hc[1] - 3.6)} Q${f(hc[0] + 4.4)} ${f(hc[1] - 5)} ${f(hc[0] + 4)} ${f(hc[1] - 8)} Q${f(hc[0])} ${f(hc[1] - 11)} ${f(hc[0] - 3.8)} ${f(hc[1] - 8)} Q${f(hc[0] - 4.2)} ${f(hc[1] - 5)} ${f(hc[0] - 6.4)} ${f(hc[1] - 3.6)}Z`);
  scarf.setAttribute('d', `M${f(hc[0] - 4.6)} ${f(hc[1] + 4.6)} Q${f(hc[0])} ${f(hc[1] + 8.4)} ${f(hc[0] + 4)} ${f(hc[1] + 4.8)} L${f(hc[0] + 4.4)} ${f(hc[1] + 7.6)} Q${f(hc[0])} ${f(hc[1] + 11)} ${f(hc[0] - 4.8)} ${f(hc[1] + 7.4)}Z`);
  const flow = tail.step(-6 - walk.speed * 0.08 * clamp(go, 0, 1) - Math.sin(t * 0.8) * 1.2 + Math.sin(t * 9) * 0.6, dt);
  scarfTail.setAttribute('d', `M${f(hc[0] - 3.6)} ${f(hc[1] + 6)} Q${f(hc[0] - 6 + flow * 0.4)} ${f(hc[1] + 9)} ${f(hc[0] - 4 + flow)} ${f(hc[1] + 16 + flow * 0.2)} L${f(hc[0] - 1 + flow * 0.9)} ${f(hc[1] + 16.6 + flow * 0.2)} Q${f(hc[0] - 3 + flow * 0.3)} ${f(hc[1] + 10)} ${f(hc[0] - 0.8)} ${f(hc[1] + 7.4)}Z`);
  const sc = nightTint('#b3412d', P); scarf.setAttribute('fill', sc); scarfTail.setAttribute('fill', sc);

  // arms: far arm swings, near arm carries the lantern and reaches for the lamp
  const legSwing = (p.feet[0].ankle[0] - 40) / (walk.stride / 2);
  const farA = armSwing[0].step(-legSwing * 16 * clamp(go, 0, 1), dt) * Math.PI / 180;
  const nearA = armSwing[1].step(legSwing * 14 * clamp(go, 0, 1), dt) * Math.PI / 180;
  const shF: Vec = [sh[0] - 1, sh[1] + 2], shN: Vec = [sh[0] + 1.6, sh[1] + 2.4];
  const elbF: Vec = [shF[0] + 17 * Math.sin(farA), shF[1] + 17 * Math.cos(farA)];
  farArm.draw([shF, elbF, [elbF[0] + 16 * Math.sin(farA + 0.25), elbF[1] + 16 * Math.cos(farA + 0.25)]], [0.2, 0.5]);

  const lift = Math.max(win(t, C[2] + 0.2, C[2] + 0.7, C[2] + 1.3, C[2] + 1.8), win(t, C[3] + 0.1, C[3] + 0.6, C[3] + 1.1, C[3] + 1.6),
    win(t, C[4] + 0.6, C[4] + 1.1, C[5] - 0.3, C[5] + 0.3), win(t, C[6] + 0.1, C[6] + 0.6, C[7] + 1.6, C[7] + 2.2));
  const lampNow = LAMPS.reduce((best, lx) => (Math.abs(lx - 16 - w.x) < Math.abs(best - 16 - w.x) ? lx : best), LAMPS[0]);
  const target: Vec = [40 + (lampNow - w.x) / SCALE * dir, 120 + (HEAD_Y + 16 - GROUND) / SCALE];
  const elbN0: Vec = [shN[0] + 17 * Math.sin(nearA), shN[1] + 17 * Math.cos(nearA)];
  const hand0: Vec = [elbN0[0] + 16 * Math.sin(nearA + 0.1), elbN0[1] + 16 * Math.cos(nearA + 0.1)];
  // while he thinks about the last drop the lantern is held in front at chest height
  const look = win(t, C[5] + 0.1, C[5] + 0.7, C[5] + 3.6, C[6] + 0.2);
  const chest: Vec = [shN[0] + 12, shN[1] + 16];
  let hand: Vec = [lerp(hand0[0], chest[0], look), lerp(hand0[1], chest[1], look)];
  hand = [lerp(hand[0], target[0], lift), lerp(hand[1], target[1], lift)];
  const elb = joint(shN, hand, 17, 16, 1);
  nearArm.draw([shN, elb, hand], [0.2, 0.4]);

  // lantern: hangs from the hand on a pendulum, tilts toward the lamp to pour, flame dims then dies
  const tilt = ease((t - (C[6] + 0.5)) / 0.6) * (1 - ease((t - (C[7] + 0.2)) / 0.6));
  const sw = lanSwing.step(-Math.cos(2 * Math.PI * phase * 2) * 1.2 * clamp(go, 0, 1), dt);
  lanG.setAttribute('transform', `translate(${pt(hand)}) rotate(${f(sw * 57.3 - tilt * 78)})`);
  lanHandle.setAttribute('d', 'M-2.6 3 Q0 -2 2.6 3');
  lanBody.setAttribute('d', 'M-4.2 3 L4.2 3 L5 12 L-5 12Z M-3.4 3 L-3.4 12 M3.4 3 L3.4 12');
  const flameLvl = t < C[5] + 1.0 ? 1 : t < C[7] + 1.4 ? lerp(1, 0.35, ease((t - C[5] - 1.0) / 0.7)) : 0.35 * (1 - smooth(smokeAt, smokeAt + 0.5, t));
  lanFlame.setAttribute('cx', '0'); lanFlame.setAttribute('cy', '8');
  lanFlame.setAttribute('ry', f(4.2 * flameLvl * (1 + 0.08 * Math.sin(t * 13)))); lanFlame.setAttribute('rx', f(2.3 * Math.max(0.2, flameLvl)));
  lanFlame.setAttribute('opacity', flameLvl < 0.02 ? '0' : '1');
  lanHalo.setAttribute('cy', '8'); lanHalo.setAttribute('opacity', f(Math.min(0.9, flameLvl * 0.9)));
  const sm = smooth(smokeAt, smokeAt + 0.3, t) * (1 - smooth(smokeAt + 0.6, smokeAt + 1.9, t));
  smoke.setAttribute('opacity', f(sm));
  smoke.setAttribute('d', `M0 6 q${f(3 + Math.sin(t * 6))} -6 0 -12 q${f(-3 + Math.sin(t * 5))} -6 ${f(1)} -12`);

  // the last drop of oil: lantern spout -> lamp three
  const dt1 = (t - (C[6] + 1.0)) / 0.5;
  if (dt1 > 0 && dt1 < 1.2 && lampNow === LAMPS[2]) {
    const sp = [w.x + dir * SCALE * (hand[0] - 40) + dir * 9, GROUND + SCALE * (hand[1] - 120) - 6];
    drop.setAttribute('cx', f(lerp(sp[0], LAMPS[2], clamp(dt1, 0, 1)))); drop.setAttribute('cy', f(lerp(sp[1], HEAD_Y - 12, clamp(dt1, 0, 1) ** 1.6)));
    drop.setAttribute('opacity', dt1 < 1 ? '1' : '0');
  } else drop.setAttribute('opacity', '0');
});
