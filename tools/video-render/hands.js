// Assigns every note of a piano MIDI file to the left or right hand by asking
// TypeSafe's Jev model, then re-asks wherever the result is physically
// impossible (a hand stretched too far, too many notes struck together,
// crossed hands).
//
// Usage: node tools/video-render/hands.js <file.mid> <out.json>
// Needs TYPESAFE_API_KEY (sent as a Bearer token) unless a proxy adds it.
'use strict';

const fs = require('fs');
const path = require('path');
const MidiParser = require('../../midi-parser-js.js');

const API = 'https://api.typesafe.ai/v1/systemone';
const MODEL = process.env.JEV_MODEL || 'jev-latest';
const WINDOW = 40; // at most this many notes asked about per request
const WINDOW_SECS = 1.5; // and at most this much music
const MEMORY = 3; // seconds: older notes no longer affect where a hand is
const LOOKAHEAD = 1.5; // seconds of music shown after the asked-about notes
const POSITION = 0.5; // seconds: a hand is where its notes of the last half second are
const MAX_SPAN = 15; // semitones one hand can hold at once (a tenth)
const REACH = 0.06; // seconds within which notes count as one chord
// shortest time a hand needs to leave its position and land `d` semitones away
const minLeapTime = d => d <= MAX_SPAN ? 0 : 0.07 + (d - MAX_SPAN) * 0.008;
const NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'];
const noteName = m => NAMES[m % 12] + (Math.floor(m / 12) - 1);
const secs = t => t.toFixed(2);

// same rules as midiLoader.js: one tempo, note on with velocity 0 is note off
function readNotes(file) {
  const midi = MidiParser.parse(new Uint8Array(fs.readFileSync(file)));
  let microsecs = 500000;
  const notes = [];
  midi.track.forEach(track => {
    let tick = 0;
    const playing = {};
    track.event.forEach(e => {
      tick += e.deltaTime;
      if (e.type === 9 && e.data[1] !== 0) {
        playing[e.data[0]] = notes.length;
        notes.push({ tick, endTick: tick + 10, midi: e.data[0] });
      } else if (e.type === 8 || e.type === 9) {
        const i = playing[e.data[0]];
        if (i !== undefined) { notes[i].endTick = tick; delete playing[e.data[0]]; }
      } else if (e.type === 255 && e.metaType === 81 && microsecs === 500000) {
        microsecs = e.data;
      }
    });
  });
  const toSec = tick => tick * microsecs * 1e-6 / midi.timeDivision;
  notes.sort((a, b) => a.tick - b.tick || a.midi - b.midi);
  notes.forEach((n, id) => Object.assign(n, { id, t: toSec(n.tick), end: toSec(n.endTick) }));
  return notes;
}

// moments: notes whose onsets are within 30 ms of each other
function moments(notes) {
  const out = [];
  notes.forEach(n => {
    const last = out[out.length - 1];
    if (last && n.t - last.t < 0.03) last.notes.push(n);
    else out.push({ t: n.t, notes: [n] });
  });
  return out;
}

const sounding = (notes, t) => notes.filter(n => n.t <= t + 0.03 && n.end > t + 0.03);

// How a pianist divides the notes. Sent once per request as part of the state.
const PIANIST_GUIDE = `You are an experienced concert pianist and piano teacher deciding which hand
plays each note of a solo piano piece, the way a careful edition would mark it.
Choose the division a pianist would find natural and comfortable, not merely
possible.

The hands:
- Each hand has five fingers, so it strikes at most five notes at the same moment.
- A hand at rest covers about a sixth to an octave comfortably. A ninth or a
  tenth is a stretch that only works for an open chord played forte, and nothing
  wider than a tenth (15 semitones) can be struck at once by one hand.
- The thumb can pass under the hand and the fingers over the thumb, so one hand
  plays scales and arpeggios smoothly across several octaves.
- Repeated notes, trills and tremolos stay in one hand unless the two hands
  clearly alternate.

How fast a hand can move:
- Within its current position a hand plays notes as fast as the fingers allow.
- Leaving that position takes time. A leap wider than a tenth needs about a
  tenth of a second, two octaves about a seventh of a second, three octaves about
  a quarter of a second. A hand cannot play a note and then, a few hundredths of
  a second later, a note two octaves away; when that happens, the other hand
  plays one of them.
- A note still held down pins its hand near that note until it is released.

How the work is shared:
- The left hand normally plays the bass line, the low chords and the
  accompaniment figures; the right hand plays the melody and the upper voices.
- The hands keep their order: the left hand stays below the right. Crossing over
  is a rare special effect, and the hands never share one key.
- In fast runs and arpeggios spanning the keyboard, each hand keeps its own
  register and the figure passes from one hand to the other at a natural point,
  usually near the middle of the keyboard.
- Inner voices go to whichever hand is closer and freer at that moment; prefer the
  division that keeps each hand in one position for longer.
- When notes are many and simultaneous, divide them so that both hands are within
  their reach, even if a hand must take a note from the middle register.`;

function describe(groups, targets, hands, notes, problems, start) {
  const lines = [
    PIANIST_GUIDE,
    '',
    'The passage (from a recorded performance, so timings are slightly uneven).',
    'Each line is one moment: time in seconds, then the notes that start then,',
    'as pitch name with duration in seconds. C4 is middle C; C5 is an octave above.',
    'Notes already given a hand are marked =L (left) or =R (right). Notes still held',
    'down from the last three seconds are listed after "held". Notes marked with',
    '#number are the ones being asked about. Only the last three seconds of music',
    'are shown, because older notes no longer affect where the hands are.',
    '',
    `When the asked-about section starts, at ${secs(start)} s, in the current draft ` +
      `${handPlaces({ t: start, id: -1 }, hands, notes, false)}.`,
    '',
  ];
  groups.forEach(g => {
    const now = g.notes.map(n => {
      const label = targets.has(n.id) ? `#${n.id} ` : '';
      const hand = !targets.has(n.id) && hands[n.id] ? `=${hands[n.id]}` : '';
      return `${label}${noteName(n.midi)}(${secs(n.end - n.t)})${hand}`;
    });
    const held = sounding(notes, g.t).filter(n => n.t < g.t - 0.03 && n.t > g.t - MEMORY)
      .map(n => noteName(n.midi) + (hands[n.id] && !targets.has(n.id) ? `=${hands[n.id]}` : ''));
    lines.push(`${secs(g.t)}: ${now.join(' ')}` + (held.length ? `   held: ${held.join(' ')}` : ''));
  });
  if (problems && problems.length) {
    lines.push('', 'The current assignment is physically impossible here:', ...problems);
  }
  return lines.join('\n');
}

// where each hand physically is when note n is struck, and where it goes
// next, from the current draft
function handPosition(n, hands, notes) {
  return handPlaces(n, hands, notes, true);
}

// where each hand is just before `n` (a note, or { t, midi: null } for a
// moment); with `detail`, also the distance to n and the hand's next note
function handPlaces(n, hands, notes, detail) {
  return ['L', 'R'].map(h => {
    const name = h === 'L' ? 'left' : 'right';
    const mine = notes.filter(m => hands[m.id] === h && m.id !== n.id);
    if (!detail) {
      const past = mine.filter(m => m.t < n.t - 0.03 && m.t > n.t - MEMORY);
      if (past.length === 0) return `the ${name} hand is free (it has not played for over ${MEMORY} seconds)`;
      const last = past[past.length - 1];
      const recent = past.filter(m => m.t > last.t - POSITION).map(m => m.midi);
      const lo = Math.min(...recent), hi = Math.max(...recent);
      return `the ${name} hand is placed around ${lo === hi ? noteName(lo) : `${noteName(lo)}–${noteName(hi)}`} ` +
        `(last struck ${secs(n.t - last.t)} s before)`;
    }
    const past = mine.filter(m => m.t < n.t - 0.03 && m.t > n.t - MEMORY);
    const next = mine.find(m => m.t > n.t + 0.03 && m.t < n.t + LOOKAHEAD);
    let where;
    if (past.length === 0) {
      where = `The ${name} hand has not played for over ${MEMORY} seconds, so it is free to go anywhere`;
    } else {
      const last = past[past.length - 1];
      const recent = past.filter(m => m.t > last.t - POSITION);
      const lo = Math.min(...recent.map(m => m.midi)), hi = Math.max(...recent.map(m => m.midi));
      const gap = n.midi < lo ? lo - n.midi : n.midi > hi ? n.midi - hi : 0;
      where = `The ${name} hand is around ${lo === hi ? noteName(lo) : `${noteName(lo)}–${noteName(hi)}`}, ` +
        `last struck ${secs(n.t - last.t)} s earlier, ` +
        (gap ? `${gap} semitones from this note` : 'already over this note');
    }
    if (next) {
      where += `, and next plays ${noteName(next.midi)} ${secs(next.t - n.t)} s later ` +
        `(${Math.abs(next.midi - n.midi)} semitones from this note)`;
    }
    return where + '.';
  }).join(detail ? ' ' : '; ');
}

let askCount = 0, sampleAt = -1;

async function ask(state, ids, notes, hands) {
  const questions = {};
  ids.forEach(id => {
    const n = notes[id];
    questions[`n${id}`] = {
      type: 'choice',
      instructions: `Which hand should play note #${id}, ${noteName(n.midi)} at ${secs(n.t)} s, ` +
        `for a comfortable, natural performance? In the current draft: ` +
        `${handPosition(n, hands, notes)} ` +
        'Judge whether each hand can reach the note in time from where it is, ' +
        'with its five fingers and its span.',
      criteria: {
        left: 'the left hand plays it',
        right: 'the right hand plays it',
      },
    };
  });
  const body = JSON.stringify({ model: MODEL, state, questions });
  // SAMPLE_REQUEST=<file> saves one request from pass 2 to read the prompt
  if (process.env.SAMPLE_REQUEST && askCount++ === sampleAt) {
    fs.writeFileSync(process.env.SAMPLE_REQUEST, JSON.stringify(JSON.parse(body), null, 1));
  }
  const headers = { 'Content-Type': 'application/json' };
  if (process.env.TYPESAFE_API_KEY) headers.Authorization = `Bearer ${process.env.TYPESAFE_API_KEY}`;
  for (let attempt = 0; ; attempt++) {
    const res = await fetch(API, { method: 'POST', headers,
      body });
    if (res.ok) {
      const { answers } = await res.json();
      return ids.map(id => answers[`n${id}`].probabilities.left);
    }
    const text = await res.text();
    if (attempt >= 3 || res.status < 500 && res.status !== 429) {
      throw new Error(`TypeSafe ${res.status}: ${text.slice(0, 300)}`);
    }
    await new Promise(r => setTimeout(r, 2000 * 2 ** attempt));
  }
}

// ask about the notes of groups[a..b), showing the MEMORY seconds before them
// and LOOKAHEAD seconds after
async function askRange(groups, a, b, hands, notes, problems) {
  const targets = new Set();
  for (let i = a; i < b; i++) groups[i].notes.forEach(n => targets.add(n.id));
  const from = groups[a].t - MEMORY, to = groups[b - 1].t + LOOKAHEAD;
  const view = groups.filter(g => g.t > from && g.t < to);
  const ids = [...targets];
  const state = describe(view, targets, hands, notes, problems, groups[a].t);
  return [ids, await ask(state, ids, notes, hands)];
}

// run async jobs with at most `limit` in flight, keeping their order
async function pool(items, limit, fn) {
  const results = new Array(items.length);
  let next = 0;
  await Promise.all(Array.from({ length: limit }, async () => {
    while (next < items.length) {
      const i = next++;
      results[i] = await fn(items[i]);
    }
  }));
  return results;
}

// windows of whole moments: at most WINDOW notes and WINDOW_SECS of music
function windows(groups) {
  const out = [];
  let a = 0, count = 0;
  groups.forEach((g, i) => {
    if (i > a && (count + g.notes.length > WINDOW || g.t - groups[a].t > WINDOW_SECS)) {
      out.push([a, i]);
      a = i;
      count = 0;
    }
    count += g.notes.length;
  });
  out.push([a, groups.length]);
  return out;
}

function findProblems(groups, hands, notes) {
  const bad = [];
  groups.forEach((g, i) => {
    // notes struck together (within REACH seconds): performance MIDI keeps keys
    // down long after they are struck, so held notes are not counted
    const now = notes.filter(n => n.t <= g.t + 0.03 && n.t > g.t - REACH);
    const left = now.filter(n => hands[n.id] === 'L').map(n => n.midi);
    const right = now.filter(n => hands[n.id] === 'R').map(n => n.midi);
    const text = [];
    [['left', left], ['right', right]].forEach(([name, ps]) => {
      if (ps.length > 5) text.push(`the ${name} hand would hold ${ps.length} notes`);
      if (ps.length && Math.max(...ps) - Math.min(...ps) > MAX_SPAN) {
        text.push(`the ${name} hand would span ${noteName(Math.min(...ps))} to ` +
          `${noteName(Math.max(...ps))} (${Math.max(...ps) - Math.min(...ps)} semitones)`);
      }
    });
    // leaps: each new note against the same hand's notes struck just before
    g.notes.forEach(n => {
      const h = hands[n.id];
      const recent = notes.filter(m => hands[m.id] === h && m.t < n.t - 0.03 && m.t > n.t - 0.3);
      const leap = recent.find(m => n.t - m.t < minLeapTime(Math.abs(n.midi - m.midi)));
      if (leap) {
        text.push(`the ${h === 'L' ? 'left' : 'right'} hand would leap from ${noteName(leap.midi)} ` +
          `to ${noteName(n.midi)} in ${secs(n.t - leap.t)} s`);
      }
    });
    if (left.length && right.length && Math.max(...left) > Math.min(...right) + 2) {
      text.push(`the hands would cross: left hand up to ${noteName(Math.max(...left))} ` +
        `while the right hand plays ${noteName(Math.min(...right))}`);
    }
    if (text.length) bad.push({ i, text: `at ${secs(g.t)} s ${text.join(', and ')}` });
  });
  return bad;
}

async function main() {
  const [file, out] = process.argv.slice(2);
  if (!file || !out) {
    console.error('usage: node hands.js <file.mid> <out.json>');
    process.exit(1);
  }
  const notes = readNotes(file);
  const groups = moments(notes);
  const hands = {}; // note id -> 'L' | 'R'
  const pLeft = {};
  const apply = (ids, probs) => ids.forEach((id, k) => {
    pLeft[id] = probs[k];
    hands[id] = probs[k] >= 0.5 ? 'L' : 'R';
  });
  console.log(`${notes.length} notes in ${groups.length} moments, model ${MODEL}`);

  // pass 1: left to right, each window sees the hands chosen before it
  const wins = windows(groups);
  for (const [k, [a, b]] of wins.entries()) {
    apply(...await askRange(groups, a, b, hands, notes));
    process.stdout.write(`  pass 1: ${k + 1}/${wins.length}\r`);
  }
  console.log(`  pass 1: ${wins.length} requests          `);

  // pass 2: re-ask every window with hands known on both sides
  sampleAt = askCount + Math.floor(wins.length / 2);
  const before = { ...hands };
  const second = await pool(wins, 6, ([a, b]) => askRange(groups, a, b, before, notes));
  second.forEach(r => apply(...r));
  const changed = notes.filter(n => before[n.id] !== hands[n.id]).length;
  console.log(`  pass 2: ${changed} notes changed hand`);

  // passes 3+: spell out each impossible spot and ask again
  for (let round = 1; round <= 4; round++) {
    const problems = findProblems(groups, hands, notes);
    console.log(`  check ${round}: ${problems.length} impossible moments`);
    if (problems.length === 0) break;
    const fixes = await pool(problems, 6, p =>
      askRange(groups, Math.max(0, p.i - 1), Math.min(groups.length, p.i + 2), hands, notes, [p.text]));
    fixes.forEach(r => apply(...r));
  }

  // last resort: split each remaining chord low/high at the point Jev finds
  // most likely among the splits both hands can actually play
  const remaining = findProblems(groups, hands, notes);
  remaining.forEach(p => {
    const t = groups[p.i].t;
    const chord = notes.filter(n => n.t <= t + 0.03 && n.t > t - REACH)
      .sort((a, b) => a.midi - b.midi);
    const playable = ps => ps.length <= 5 && (ps.length < 2 || ps[ps.length - 1] - ps[0] <= MAX_SPAN);
    let best = null;
    for (let k = 0; k <= chord.length; k++) {
      const lh = chord.slice(0, k).map(n => n.midi), rh = chord.slice(k).map(n => n.midi);
      if (!playable(lh) || !playable(rh)) continue;
      const score = chord.reduce((a, n, j) => a +
        Math.log(Math.max(1e-6, j < k ? pLeft[n.id] : 1 - pLeft[n.id])), 0);
      if (!best || score > best.score) best = { k, score };
    }
    if (best) chord.forEach((n, j) => { hands[n.id] = j < best.k ? 'L' : 'R'; });
  });
  // then leaps and anything else left: move single notes to the other hand
  // when that removes problems nearby, preferring moves Jev finds least unlikely
  const near = t => groups.filter(g => g.t > t - 0.6 && g.t < t + 0.6);
  let moved = 0;
  for (let round = 0; round < 20; round++) {
    const left = findProblems(groups, hands, notes);
    if (left.length === 0) break;
    let improved = false;
    left.forEach(p => {
      const t = groups[p.i].t;
      const before = findProblems(near(t), hands, notes).length;
      let best = null;
      notes.filter(n => n.t > t - 0.3 && n.t < t + 0.3).forEach(n => {
        const was = hands[n.id];
        hands[n.id] = was === 'L' ? 'R' : 'L';
        const after = findProblems(near(t), hands, notes).length;
        const cost = -Math.log(Math.max(1e-6, hands[n.id] === 'L' ? pLeft[n.id] : 1 - pLeft[n.id]));
        if (after < before && (!best || after < best.after || after === best.after && cost < best.cost)) {
          best = { n, after, cost };
        }
        hands[n.id] = was;
      });
      if (best) {
        hands[best.n.id] = hands[best.n.id] === 'L' ? 'R' : 'L';
        moved++;
        improved = true;
      }
    });
    if (!improved) break;
  }
  console.log(`  repair: ${remaining.length} chords split by reach, ${moved} notes moved, ` +
    `${findProblems(groups, hands, notes).length} impossible moments left`);

  const left = notes.filter(n => hands[n.id] === 'L').length;
  fs.writeFileSync(out, JSON.stringify({
    source: path.basename(file),
    model: MODEL,
    left, right: notes.length - left,
    // key: "<start tick>:<MIDI pitch>" -> hand, as harness.js looks it up
    hands: Object.fromEntries(notes.map(n => [`${n.tick}:${n.midi}`, hands[n.id]])),
    confidence: Object.fromEntries(notes.map(n =>
      [`${n.tick}:${n.midi}`, Math.round(Math.abs(pLeft[n.id] - 0.5) * 200) / 100])),
  }, null, 1));
  console.log(`left hand ${left} notes, right hand ${notes.length - left} -> ${out}`);
}

main().catch(e => { console.error(e); process.exit(1); });
