// Prints a progress bar per job and an overall estimate for running renders.
// Usage: node tools/video-render/progress.js <outdir>
'use strict';

const fs = require('fs');
const path = require('path');

const dir = process.argv[2];
const bar = (fraction, width) => {
  const full = Math.round(Math.min(1, fraction) * width);
  return '█'.repeat(full) + '░'.repeat(width - full);
};
const clock = s => {
  s = Math.max(0, Math.round(s));
  const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60;
  return h ? `${h}h ${String(m).padStart(2, '0')}m` : `${m}m ${String(s % 60).padStart(2, '0')}s`;
};

let done = 0, total = 0, remaining = 0;
const lines = [];
fs.readdirSync(dir).filter(f => /^progress-\d+\.json$/.test(f)).forEach(f => {
  const { jobs } = JSON.parse(fs.readFileSync(path.join(dir, f)));
  // a worker renders its jobs one after another: estimate queued jobs
  // from the speed of what it has rendered so far
  const rendered = jobs.reduce((a, j) => a + j.done, 0);
  const spent = jobs.reduce((a, j) => a + j.seconds, 0);
  const rate = spent > 0 ? rendered / spent : 0;
  let workerLeft = 0;
  jobs.forEach(j => {
    const fraction = j.frames ? j.done / j.frames : 0;
    const jobRate = j.seconds > 0 && j.done > 0 ? j.done / j.seconds : rate;
    const left = j.finished ? 0 : (jobRate ? (j.frames - j.done) / jobRate : NaN);
    workerLeft += left;
    done += j.done;
    total += j.frames;
    const state = j.finished ? 'done' : j.done ? `~${clock(left)} left` : 'queued';
    lines.push(`${bar(fraction, 20)} ${String(Math.round(fraction * 100)).padStart(3)}%  ` +
      `${j.name.padEnd(30)} ${state}`);
  });
  remaining = Math.max(remaining, workerLeft); // workers run in parallel
});

console.log(lines.join('\n'));
console.log(`\nOverall ${bar(total ? done / total : 0, 30)} ${Math.round(100 * done / (total || 1))}%` +
  (Number.isFinite(remaining) && remaining > 0 ? ` · about ${clock(remaining)} to go` : ''));
