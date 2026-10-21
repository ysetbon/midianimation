// Video jobs: every animation option the MuVis brush offers.
'use strict';

const fs = require('fs');
const path = require('path');

const STATES = path.resolve(__dirname, '../../states');

// values mirror reducers/brushes.js
const SHAPES = [['Rectangle', '1'], ['Circle', '2'], ['Triangle', '3'], ['Blob', '4']];
const PLAY = [['Mask', '1'], ['Flip', '2'], ['On/Off', '3'], ['Flash', '4']];
const CONNECT = [['None', '1'], ['Line', '2'], ['Float', '3'], ['Bend', '4']];
const COLOR = [['Uniform', 'UNIFORM'], ['Voice', 'VOICE'], ['Pitch', 'PITCH']];

const BACKGROUND = [0.043, 0.043, 0.043];
// bass, tenor, alto, soprano (see registerVoice in harness.js)
const VOICES = [[1, 0.35, 0.35], [1, 0.75, 0.2], [0.35, 1, 0.5], [0.4, 0.55, 1]];

const loadState = name => JSON.parse(fs.readFileSync(path.join(STATES, name + '.json')));

function buildJobs({ defaults, pieceLength, pieceStart }) {
  // a neutral base so each option can be shown on its own
  const base = {
    ...defaults,
    size: 1.6,
    sizeCurve: 0.3,
    timeCurve1: 0.3,
    timeCurve2: 1.0, // 1.0 disables the time lens
    leftColor: [0.3, 0.42, 1],
    rightColor: [1, 1, 1],
    connectDistance: 0.3,
  };
  const scene = (brush, extra) => ({
    brushes: [{ ...base, id: 0, ...brush }],
    voices: VOICES,
    background: BACKGROUND,
    timeSpan: 7,
    assign: 'all',
    ...extra,
  });

  const layered = scene({}, {
    brushes: [
      { ...base, id: 0, name: 'Bass', shape: '4', playMode: '4', connectMode: '3',
        size: 5, sizeCurve: 0.2, timeZoom: 0.7, connectDistance: 0.6,
        leftColor: [0.55, 0.25, 0.9], rightColor: [1, 1, 1] },
      { ...base, id: 1, name: 'Treble', shape: '3', playMode: '4', connectMode: '1',
        size: 1.8, sizeCurve: 0.9, leftColor: [1, 0.85, 0.2], rightColor: [1, 1, 1] },
    ],
    assign: [{ below: 60, brush: 0 }, { brush: 1 }],
  });

  const presetScene = name => {
    const s = loadState(name);
    const assign = name === 'rameau'
      ? [{ below: 52, brush: 3 }, { below: 72, brush: 0 }, { brush: 2 }]
      : 'all';
    return {
      brushes: s.brushes,
      voices: name === 'kyrie' ? s.voices.map(v => v.voiceColor) : VOICES,
      background: s.backgroundColor,
      timeSpan: s.timeSpan,
      assign,
    };
  };

  const presets = {
    tristan: ['Preset: Tristan und Isolde', 'blob · flash · float · slow scroll', presetScene('tristan')],
    kyrie: ['Preset: Kyrie', 'circle · voice colours · float', presetScene('kyrie')],
    rameau: ['Preset: Rameau', '3 layered brushes on red', presetScene('rameau')],
  };

  const full = { fps: 30, duration: pieceLength, pieceStart };
  const jobs = [];

  // 1. one full-HD walk through every option, in sequence
  const showcase = [
    ...SHAPES.map(([n, v]) => ['Shape: ' + n, 'note shape', scene({ shape: v })]),
    ...PLAY.map(([n, v]) => ['Play mode: ' + n, {
      '1': 'colour wipes at the play head', '2': 'whole note flips colour',
      '3': 'lit only while sounding', '4': 'flash, then fade back' }[v],
      scene({ shape: '1', playMode: v })]),
    ...COLOR.map(([n, v]) => ['Colour mode: ' + n, {
      UNIFORM: 'one colour pair for the brush', VOICE: 'colour per voice (4 registers)',
      PITCH: 'colour by pitch class (circle of fifths)' }[v],
      scene({ shape: '2', colorMode: v })]),
    ...CONNECT.map(([n, v]) => ['Connect: ' + n, {
      '1': 'notes stand alone', '2': 'line mode (no visual change in this renderer)',
      '3': 'note floats into the next one', '4': 'note bends towards the next pitch' }[v],
      scene({ shape: '4', size: 2.4, connectMode: v, colorMode: 'VOICE' })]),
    ['Connect: Float, appear back off', 'played notes vanish after floating',
      scene({ shape: '4', size: 2.4, connectMode: '3', appearBack: '0', colorMode: 'VOICE' })],
    ['Size curve', 'notes swell when struck',
      scene({ shape: '2', sizeCurve: 1.6, colorMode: 'PITCH' })],
    ['Time curve', 'lens magnifies time around the play head',
      scene({ shape: '1', timeCurve1: 0.6, timeCurve2: 4, colorMode: 'VOICE' })],
    ['Time zoom 2×', 'brush scrolls twice as fast',
      scene({ shape: '3', timeZoom: 2, size: 2 })],
    ['Layered brushes', 'bass: blob + float · treble: triangle + flash', layered],
    ...Object.values(presets),
  ];
  const step = pieceLength / showcase.length;
  jobs.push({
    ...full, name: '01_showcase_all_options', width: 1920, height: 1080,
    panels: [{ x: 0, y: 0, w: 1920, h: 1080, labelSize: 38,
      segments: showcase.map(([label, sublabel, s], i) => ({
        until: (i + 1) * step, label, sublabel, scene: s })) }],
  });

  // 2./3. 4x4 grids over the full piece
  const grid = (name, rows, cols, make) => {
    const w = 1920 / cols, h = 1080 / rows;
    const panels = [];
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const [label, s] = make(r, c);
      panels.push({ x: c * w, y: r * h, w, h, labelSize: 15,
        segments: [{ until: Infinity, label, scene: s }] });
    }
    return { ...full, name, width: 1920, height: 1080, crf: 21, panels };
  };

  jobs.push(grid('02_grid_shape_x_playmode', 4, 4, (r, c) => [
    `${SHAPES[c][0]} · ${PLAY[r][0]}`,
    scene({ shape: SHAPES[c][1], playMode: PLAY[r][1], size: 2 }, { timeSpan: 5 })]));

  jobs.push(grid('03_grid_shape_x_connect', 4, 4, (r, c) => [
    `${SHAPES[c][0]} · connect ${CONNECT[r][0]}`,
    scene({ shape: SHAPES[c][1], connectMode: CONNECT[r][1], size: 2.4,
      colorMode: 'VOICE' }, { timeSpan: 5 })]));

  const effects = [
    ['Colour: Uniform', scene({ shape: '2', size: 2.2 })],
    ['Colour: Voice', scene({ shape: '2', size: 2.2, colorMode: 'VOICE' })],
    ['Colour: Pitch', scene({ shape: '2', size: 2.2, colorMode: 'PITCH' })],
    ['Size curve 1.6', scene({ shape: '2', size: 2, sizeCurve: 1.6, colorMode: 'PITCH' })],
    ['Time curve (lens)', scene({ shape: '1', timeCurve1: 0.6, timeCurve2: 4, colorMode: 'VOICE' })],
    ['Time zoom 2×', scene({ shape: '3', timeZoom: 2, size: 2.2 })],
    ['Float · appear back on', scene({ shape: '4', size: 2.6, connectMode: '3', colorMode: 'VOICE' })],
    ['Float · appear back off', scene({ shape: '4', size: 2.6, connectMode: '3', appearBack: '0', colorMode: 'VOICE' })],
    ['Layered brushes', layered],
  ];
  jobs.push(grid('04_grid_colour_and_effects', 3, 3, (r, c) => effects[r * 3 + c]));

  // 5.-7. the three example projects' brushes applied to this MIDI
  Object.entries(presets).forEach(([key, [label, sublabel, s]], i) => {
    jobs.push({
      ...full, name: `0${5 + i}_preset_${key}`, width: 1280, height: 720,
      panels: [{ x: 0, y: 0, w: 1280, h: 720, labelSize: 24,
        segments: [{ until: Infinity, label, sublabel, scene: s }] }],
    });
  });

  // 8. every combination of shape x play mode x connect mode x colour mode,
  // one video per shape (48 combinations each)
  const clip = 3;
  SHAPES.forEach(([shapeName, shape], si) => {
    const combos = [];
    PLAY.forEach(p => CONNECT.forEach(c => COLOR.forEach(col => combos.push([p, c, col]))));
    jobs.push({
      fps: 30, pieceStart, loop: pieceLength,
      name: `08${'abcd'[si]}_catalog_${shapeName.toLowerCase()}`,
      width: 1280, height: 720, crf: 23,
      duration: combos.length * clip,
      panels: [{ x: 0, y: 0, w: 1280, h: 720, labelSize: 24,
        segments: combos.map(([p, c, col], i) => ({
          until: (i + 1) * clip,
          label: `${shapeName} · ${p[0]} · connect ${c[0]} · colour ${col[0]}`,
          sublabel: `combination ${si * combos.length + i + 1} / ${combos.length * SHAPES.length}`,
          scene: scene({ shape, playMode: p[1], connectMode: c[1],
            colorMode: col[1], size: 2 }),
        })) }],
    });
  });

  return jobs;
}

module.exports = { buildJobs };
