// Step 7: thumbnails as HTML pages rendered to 1280x720 PNG. Usage: node make_thumbs.cjs
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const tokens = fs.readFileSync(path.join(__dirname, '../../brand/tokens.css'), 'utf8');
const T = { en: ['WHY BLUE?', 'NOT PAINTED. GLOWING.'], hi: ['नीला क्यों?', 'रंगा नहीं. चमकता है.'] };
const page = (words, v) => `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@800&display=block" rel="stylesheet">
<style>${tokens}
 html,body{margin:0;width:1280px;height:720px;overflow:hidden;background:var(--bg);font-family:var(--font-display)}
 .sky{position:absolute;left:${v ? 560 : -140}px;top:${v ? 150 : 170}px;width:1000px;height:1000px;border-radius:50%;background:var(--accent)}
 .sun{position:absolute;left:${v ? 930 : 250}px;top:${v ? 250 : 270}px;width:230px;height:230px;border-radius:50%;background:var(--sun);box-shadow:0 0 0 26px rgba(255,246,216,.25)}
 h1{position:absolute;${v ? 'left:70px' : 'right:70px;text-align:right'};top:${v ? 150 : 190}px;width:${v ? 600 : 560}px;margin:0;font-size:${v ? 112 : 150}px;line-height:1.02;font-weight:800;color:var(--text)}
 h1 b{color:var(--accent-2)}
</style></head><body><div class="sky"></div><div class="sun"></div><h1>${words.replace(/(\S+)$/, '<b>$1</b>')}</h1></body></html>`;
(async () => {
  const b = await chromium.launch();
  for (const lang of ['en', 'hi']) for (const v of [0, 1]) {
    const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
    await p.setContent(page(T[lang][v], v)); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
    fs.mkdirSync(path.join(__dirname, 'out', lang), { recursive: true });
    await p.screenshot({ path: path.join(__dirname, 'out', lang, `thumbnail-${v + 1}.png`) }); await p.close();
  }
  await b.close();
})();
