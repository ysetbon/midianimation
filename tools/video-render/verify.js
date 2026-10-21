// Checks that the fast-quad vertex patch in harness.js is pixel-identical to
// the repo's original renderer, for every scene of every job.
// Usage: node tools/video-render/verify.js <file.mid>
'use strict';

const fs = require('fs');
const http = require('http');
const path = require('path');
const { chromium } = require('playwright');
const { buildJobs } = require('./jobs');

const ROOT = path.resolve(__dirname, '../..');

async function main() {
  const midi = fs.readFileSync(process.argv[2]).toString('base64');
  const server = http.createServer((req, res) => {
    const file = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
    if (!file.startsWith(ROOT) || !fs.existsSync(file)) { res.writeHead(404); return res.end(); }
    res.end(fs.readFileSync(file));
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const url = `http://127.0.0.1:${server.address().port}/tools/video-render/harness.html`;
  const browser = await chromium.launch({
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
  });

  const open = async fast => {
    const page = await browser.newPage();
    await page.addInitScript(f => { window.fastQuads = f; }, fast);
    await page.goto(url);
    return [page, await page.evaluate(b => harness.loadMidi(b), midi)];
  };
  const [slow, info] = await open(false);
  const [fast] = await open(true);
  const defaults = await slow.evaluate(() => harness.defaults());
  const jobs = buildJobs({ defaults, pieceLength: info.end + 4.5, pieceStart: -1.5 });

  // every distinct scene, rendered alone in a 640x360 panel
  const scenes = [];
  jobs.forEach(j => j.panels.forEach(p => p.segments.forEach(s =>
    scenes.push([`${j.name}: ${s.label}`, s.scene]))));
  const times = [0.5, 8.3, 21.7, 40.1, 63.9, 88.4, 101.2];

  let failures = 0;
  for (const [name, scene] of scenes) {
    const job = { width: 640, height: 360, fps: 10, pieceStart: 0,
      panels: [{ x: 0, y: 0, w: 640, h: 360, segments: [{ until: Infinity, scene }] }] };
    const sums = [];
    for (const page of [slow, fast]) {
      await page.evaluate(j => harness.setupJob(j), job);
      sums.push(await page.evaluate(ts => ts.map(t => harness.checksum(t * 10)), times));
      await page.evaluate(() => harness.destroy());
    }
    const same = JSON.stringify(sums[0]) === JSON.stringify(sums[1]);
    if (!same) failures++;
    console.log(same ? 'ok  ' : 'DIFF', name, sums[0].map(s => s[1]).join(','));
  }
  console.log(`${scenes.length - failures}/${scenes.length} scenes identical`);
  await browser.close();
  server.close();
  process.exit(failures ? 1 : 0);
}

main().catch(e => { console.error(e); process.exit(1); });
