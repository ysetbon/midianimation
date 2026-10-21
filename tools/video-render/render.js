// Offline video renderer for MuVis.
//
// Usage: node tools/video-render/render.js <file.mid> <outdir> [job names...]
//
// Uses the GPU when Chromium can get one; GL=cpu forces software rendering
// (SwiftShader) and HEADED=1 opens a visible window, which some systems need
// before Chromium will use the GPU.
//
// Serves the repo over HTTP, drives the real WebGL renderer in headless
// Chromium (Playwright), pipes raw frames into ffmpeg and muxes audio
// synthesised from the same MIDI file with FluidSynth.
'use strict';

const fs = require('fs');
const http = require('http');
const path = require('path');
const { spawn, execFileSync } = require('child_process');
const { chromium } = require('playwright');
const { buildJobs } = require('./jobs');

const ROOT = path.resolve(__dirname, '../..');
const SOUNDFONTS = [
  process.env.SOUNDFONT,
  '/usr/share/sounds/sf2/FluidR3_GM.sf2',
  '/usr/share/soundfonts/FluidR3_GM.sf2',
  '/usr/share/sounds/sf2/default-GM.sf2',
  '/usr/share/soundfonts/default.sf2',
  '/opt/homebrew/share/soundfonts/default.sf2',
  '/usr/local/share/soundfonts/default.sf2',
].filter(Boolean);
const LEAD_IN = 1.5; // seconds before the first note
const TAIL = 3.0; // seconds after the last note

const mime = { '.html': 'text/html', '.js': 'application/javascript',
  '.json': 'application/json', '.css': 'text/css' };

let sink = null; // writable stream of the current ffmpeg process

function startServer() {
  const server = http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/frame') {
      req.on('data', chunk => {
        if (!sink.write(chunk)) {
          req.pause();
          sink.once('drain', () => req.resume());
        }
      });
      req.on('end', () => { res.writeHead(200); res.end(); });
      return;
    }
    const file = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
    if (!file.startsWith(ROOT) || !fs.existsSync(file)) {
      res.writeHead(404); res.end(); return;
    }
    res.writeHead(200, { 'Content-Type': mime[path.extname(file)] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve(server)));
}

function synthAudio(midiFile, outdir, start, length) {
  const raw = path.join(outdir, `audio_raw_${process.pid}.wav`);
  const windowed = path.join(outdir, `audio_${process.pid}.wav`);
  const soundfont = SOUNDFONTS.find(f => fs.existsSync(f));
  try {
    if (!soundfont) throw new Error('no soundfont found, set SOUNDFONT=/path/to/file.sf2');
    execFileSync('fluidsynth', ['-ni', '-q', '-g', '0.8', '-r', '48000',
      '-F', raw, soundfont, midiFile]);
  } catch (e) {
    console.warn(`No audio (${e.message.split('\n')[0]}), rendering silent videos`);
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'lavfi',
      '-i', 'anullsrc=r=48000:cl=stereo', '-t', String(length), windowed]);
    return windowed;
  }
  // shift so that video time 0 == piece time `start` (negative = lead-in)
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', raw, '-af',
    `adelay=${Math.round(-start * 1000)}:all=1,apad,atrim=0:${length}`,
    windowed]);
  fs.unlinkSync(raw);
  return windowed;
}

function startEncoder(job, audio, out, offset) {
  const args = ['-y', '-loglevel', 'error',
    '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(job.fps), '-i', '-'];
  if (job.loop) args.push('-stream_loop', '-1');
  args.push('-ss', String(offset), '-i', audio,
    '-map', '0:v', '-map', '1:a',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', String(job.crf || 20),
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
    '-c:a', 'aac', '-b:a', '192k', '-shortest', out);
  const proc = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((resolve, reject) =>
    proc.on('exit', code => code === 0 ? resolve() : reject(new Error('ffmpeg ' + code))));
  return { stdin: proc.stdin, done };
}

async function main() {
  const [midiFile, outdir, ...only] = process.argv.slice(2);
  if (!midiFile || !outdir) {
    console.error('usage: node render.js <file.mid> <outdir> [job names...]');
    process.exit(1);
  }
  fs.mkdirSync(outdir, { recursive: true });

  const server = await startServer();
  const base = `http://127.0.0.1:${server.address().port}`;
  const software = process.env.GL === 'cpu';
  const browser = await chromium.launch({
    channel: 'chromium', // full Chromium; its headless mode can use the GPU
    headless: process.env.HEADED !== '1',
    args: software
      ? ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']
      : ['--enable-gpu', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader'],
  });

  const midiBase64 = fs.readFileSync(midiFile).toString('base64');
  const page = await browser.newPage();
  page.on('pageerror', e => console.error('page error:', e.message));
  await page.goto(`${base}/tools/video-render/harness.html`);
  const info = await page.evaluate(b64 => harness.loadMidi(b64), midiBase64);
  const defaults = await page.evaluate(() => harness.defaults());
  const gpu = await page.evaluate(() => harness.glInfo());
  console.log(`WebGL: ${gpu}`);
  if (!software && /swiftshader|llvmpipe|software/i.test(gpu))
    console.warn('No GPU in use, rendering will be slow. Try HEADED=1.');
  await page.close();
  console.log(`MIDI: ${info.count} notes, ${info.end.toFixed(1)}s`);

  const pieceStart = -LEAD_IN;
  const pieceLength = info.end + LEAD_IN + TAIL;
  const audio = synthAudio(midiFile, outdir, pieceStart, pieceLength);

  const allJobs = buildJobs({ defaults, pieceLength, pieceStart, midi: info });
  const unknown = only.filter(n => !allJobs.some(j => j.name === n));
  if (unknown.length) {
    console.error(`Unknown job(s): ${unknown.join(', ')}\nJobs: ${allJobs.map(j => j.name).join(', ')}`);
    process.exit(1);
  }
  const jobs = allJobs
    .filter(j => only.length === 0 || only.includes(j.name))
    .map(j => ({ quality: 0.95, ...j }));

  // per-worker progress file, read by progress.js
  const progressFile = path.join(outdir, `progress-${process.pid}.json`);
  const progress = { jobs: jobs.map(j => ({ name: j.name,
    frames: Math.round(j.duration * j.fps), done: 0, seconds: 0 })) };
  const saveProgress = () => fs.writeFileSync(progressFile, JSON.stringify(progress));
  saveProgress();

  for (const [index, job] of jobs.entries()) {
    const out = path.join(outdir, job.name + '.mp4');
    // START_SECONDS / MAX_SECONDS render a sub-range, handy for previews
    const first = Math.round((Number(process.env.START_SECONDS) || 0) * job.fps);
    const seconds = Math.min(job.duration, Number(process.env.MAX_SECONDS) || Infinity);
    const frames = Math.min(Math.round(job.duration * job.fps), first + Math.round(seconds * job.fps));
    const started = Date.now();
    console.log(`${job.name}: ${job.width}x${job.height}, ${frames} frames`);

    const enc = startEncoder(job, audio, out, first / job.fps);
    sink = enc.stdin;

    const jobPage = await browser.newPage();
    jobPage.on('pageerror', e => console.error('page error:', e.message));
    await jobPage.goto(`${base}/tools/video-render/harness.html`);
    await jobPage.evaluate(b64 => harness.loadMidi(b64), midiBase64);
    await jobPage.evaluate(j => harness.setupJob(j), job);

    const batch = 60;
    for (let f = first; f < frames; f += batch) {
      await jobPage.evaluate(([a, b]) => harness.renderFrames(a, b),
        [f, Math.min(frames, f + batch)]);
      Object.assign(progress.jobs[index], { frames: frames - first,
        done: Math.min(frames, f + batch) - first, seconds: (Date.now() - started) / 1000 });
      saveProgress();
    }
    await jobPage.evaluate(() => harness.destroy());
    await jobPage.close();
    sink.end();
    await enc.done;
    progress.jobs[index].finished = true;
    saveProgress();
    console.log(`  done in ${((Date.now() - started) / 1000).toFixed(0)}s -> ${out}`);
  }

  await browser.close();
  server.close();
  fs.unlinkSync(audio);
}

main().catch(e => { console.error(e); process.exit(1); });
