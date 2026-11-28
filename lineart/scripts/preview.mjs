// Contact frames of a scene at given seconds (stepped deterministically): node scripts/preview.mjs <scene_id> <sec> [<sec> ...]
// Starts nothing: run `npx vite --port 5199` first (or let shorts.lineart.build.Server do it). Output: /tmp/lineart_preview/<scene>_<sec>.png
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
const [scene, ...secs] = process.argv.slice(2);
if (!scene || !secs.length) { console.error('usage: preview.mjs <scene_id> <seconds...>'); process.exit(1); }
mkdirSync('/tmp/lineart_preview', { recursive: true });
const b = await chromium.launch({ args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 450, height: 800 } });
const errs = [];
p.on('pageerror', (e) => errs.push(e.message));
await p.goto(`http://127.0.0.1:5199/scenes/${scene}/?debug&capture`);
await p.waitForFunction(() => window.__step, null, { timeout: 15000 });
let t = 0;
for (const s of secs.map(Number)) { await p.evaluate((d) => window.__step(d), s - t); t = s; await p.screenshot({ path: `/tmp/lineart_preview/${scene}_${s}.png` }); console.log('frame', s); }
if (errs.length) { console.error('PAGE ERRORS:', errs.slice(0, 5)); process.exitCode = 1; }
await b.close();
