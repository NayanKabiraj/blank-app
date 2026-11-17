// Render single frames of an engine config to PNG files: node still.cjs <cfg.json>   (cfg.stills = [{t, path}])
// Used for thumbnails. Same engine, same page as render.cjs, one browser, no video.
const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const ROOT = __dirname;
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2' };
const server = http.createServer((q, s) => {
  const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { s.writeHead(404); return s.end(); }
  s.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(s);
});
(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-dev-shm-usage'] });
  const page = await browser.newPage({ viewport: { width: cfg.width, height: cfg.height }, deviceScaleFactor: 1 });
  page.on('pageerror', e => { console.error('page error:', e.message); process.exitCode = 1; });
  await page.goto(`http://127.0.0.1:${server.address().port}/engine/index.html`);
  await page.waitForFunction(() => window.sceneReady === true, null, { timeout: 120000 });
  await page.evaluate(c => window.setup(c), cfg);
  for (const s of cfg.stills) { await page.evaluate(t => window.renderFrame(t), s.t); await page.screenshot({ path: s.path, type: 'png' }); }
  const rep = await page.evaluate(() => window.getReport());
  if (rep.textOverflow.length) console.warn('text overflow:', rep.textOverflow.join(','));
  await browser.close(); server.close();
})().catch(e => { console.error(e); process.exit(1); });
