// Render the 3D cartoon track: node render.cjs <config.json> <out.mp4>
// Serves this folder on localhost, drives scene.html frame by frame in headless Chromium
// (software WebGL, no GPU needed) and pipes JPEG frames into FFmpeg.
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const [, , cfgPath, outPath] = process.argv;
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const FPS = cfg.fps || 30;
const ROOT = __dirname;
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.txt': 'text/plain' };

const server = http.createServer((req, res) => {
  const file = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const url = `http://127.0.0.1:${server.address().port}/scene.html`;
  // One browser per worker: software WebGL runs in each browser's single GPU process,
  // so pages sharing one browser don't render any faster.
  const launch = () => chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const frames = Math.ceil(cfg.total * FPS);
  const workers = Math.max(1, Math.min(cfg.workers || 3, 8));
  const per = Math.ceil(frames / workers);
  const t0 = Date.now();
  const parts = await Promise.all(Array.from({ length: workers }, async (_, w) => {
    const from = w * per, to = Math.min(frames, from + per);
    const part = `${outPath}.part${w}.mp4`;
    const browser = await launch();
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
    page.on('pageerror', e => { console.error('page error:', e.message); process.exitCode = 1; });
    await page.goto(url);
    await page.waitForFunction(() => window.sceneReady === true);
    await page.evaluate(c => window.setup(c), cfg);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg',
      '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', part], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = from; f < to; f++) {
      await page.evaluate(t => window.renderFrame(t), f / FPS);
      const jpg = await page.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(jpg)) await new Promise(r => ff.stdin.once('drain', r));
      if (w === 0 && (f - from) % 100 === 0) console.log(`cartoon3d: worker 0 at ${f - from}/${to - from} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
    }
    ff.stdin.end();
    await new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error('ffmpeg exited ' + c)))));
    await browser.close();
    return part;
  }));
  const list = `${outPath}.parts.txt`;
  fs.writeFileSync(list, parts.map(p => `file '${path.resolve(p)}'`).join('\n'));
  await new Promise((res, rej) => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', outPath],
    { stdio: 'inherit' }).on('close', c => (c === 0 ? res() : rej(new Error('concat failed')))));
  parts.forEach(p => fs.unlinkSync(p)); fs.unlinkSync(list);
  server.close();
  console.log(`cartoon3d: ${frames} frames with ${workers} workers in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
})().catch(e => { console.error(e); process.exit(1); });
