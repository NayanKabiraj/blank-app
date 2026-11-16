// Render a manifest-driven video track: node render.cjs <cfg.json> <out.mp4>
// Serves this folder on localhost, drives engine/index.html frame by frame in headless Chromium (software WebGL) and pipes
// JPEG frames into FFmpeg. Frames are split across parallel browsers. cfg.sample = N renders only every Nth frame
// (a "preflight": catches errors and text overflow without producing a video) and prints a JSON report.
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const [, , cfgPath, outPath] = process.argv;
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const FPS = cfg.fps || 30, VW = cfg.width, VH = cfg.height;
const ROOT = __dirname;
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2', '.json': 'application/json' };

const server = http.createServer((req, res) => {
  const file = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});

const ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-dev-shm-usage'];

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const url = `http://127.0.0.1:${server.address().port}/engine/index.html`;
  const total = Math.ceil(cfg.total * FPS), sample = cfg.sample || 0;
  const frames = sample ? Array.from({ length: Math.ceil(total / sample) }, (_, i) => Math.min(total - 1, i * sample)) : Array.from({ length: total }, (_, i) => i);
  const workers = Math.max(1, Math.min(cfg.workers || 3, 8)), per = Math.ceil(frames.length / workers), t0 = Date.now();
  const reports = [];
  const parts = await Promise.all(Array.from({ length: workers }, async (_, w) => {
    const list = frames.slice(w * per, (w + 1) * per); if (!list.length) return null;
    const part = sample ? null : `${outPath}.part${w}.mp4`;
    const browser = await chromium.launch({ args: ARGS });
    const page = await browser.newPage({ viewport: { width: VW, height: VH }, deviceScaleFactor: 1 });
    page.on('pageerror', e => { console.error('page error:', e.message); process.exitCode = 1; });
    page.on('console', m => { if (m.type() === 'error') console.error('browser:', m.text()); });
    await page.goto(url);
    await page.waitForFunction(() => window.sceneReady === true, null, { timeout: 120000 });
    await page.evaluate(c => window.setup(c), cfg);
    const ff = part ? spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', String(cfg.crf || 18), '-pix_fmt', 'yuv420p', part], { stdio: ['pipe', 'inherit', 'inherit'] }) : null;
    for (let k = 0; k < list.length; k++) {
      await page.evaluate(t => window.renderFrame(t), list[k] / FPS);
      if (ff) {
        const jpg = await page.screenshot({ type: 'jpeg', quality: cfg.jpegQuality || 92 });
        if (!ff.stdin.write(jpg)) await new Promise(r => ff.stdin.once('drain', r));
      }
      if (w === 0 && k % 50 === 0) console.log(`director: worker 0 at ${k}/${list.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
    }
    if (cfg.stills) for (const s of cfg.stills) { if (list.includes(Math.round(s.t * FPS))) { await page.evaluate(t => window.renderFrame(t), s.t); await page.screenshot({ path: s.path, type: 'png' }); } }
    reports.push(await page.evaluate(() => window.getReport()));
    if (ff) { ff.stdin.end(); await new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error('ffmpeg exited ' + c))))); }
    await browser.close();
    return part;
  }));
  const rep = { frames: reports.reduce((a, r) => a + r.frames, 0), textOverflow: [...new Set(reports.flatMap(r => r.textOverflow))], seconds: (Date.now() - t0) / 1000 };
  if (sample) { fs.writeFileSync(outPath, JSON.stringify(rep)); }
  else {
    const list = `${outPath}.parts.txt`;
    fs.writeFileSync(list, parts.filter(Boolean).map(p => `file '${path.resolve(p)}'`).join('\n'));
    await new Promise((res, rej) => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', outPath], { stdio: 'inherit' }).on('close', c => (c === 0 ? res() : rej(new Error('concat failed')))));
    parts.filter(Boolean).forEach(p => fs.unlinkSync(p)); fs.unlinkSync(list);
    fs.writeFileSync(`${outPath}.report.json`, JSON.stringify(rep));
  }
  server.close();
  console.log(`director: ${rep.frames} frames, ${workers} workers, ${rep.seconds.toFixed(0)}s${rep.textOverflow.length ? ', text overflow: ' + rep.textOverflow.join(',') : ''}`);
})().catch(e => { console.error(e); process.exit(1); });
