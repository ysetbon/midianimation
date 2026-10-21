// Browser side of the offline video renderer.
// Uses the repo's own midiLoader and WebGL renderer, composites one or more
// panels onto a 2D canvas and streams raw RGBA frames to the node server.
const harness = (() => {
  'use strict';

  // Speed-up for software WebGL: the repo's vertex shader draws every note as
  // a square quad (as tall as it is wide), so most fragments are empty. Clamp
  // the quad vertically to the pitch range the note can reach (its own pitch,
  // plus the next note's pitch for connect modes, plus the maximum size).
  // The fragment shader is untouched, so covered pixels are identical.
  const shaderSource = WebGLRenderingContext.prototype.shaderSource;
  WebGLRenderingContext.prototype.shaderSource = function(shader, src) {
    if (window.fastQuads !== false && src.startsWith('// vertex shader')) {
      src = src
        .replace('varying float v_size;',
          'uniform vec3 u_next_note;\nuniform mediump int u_conn_mode;\n' +
          'varying float v_size;')
        .replace(
          'gl_Position = vec4(a_position * u_vertex_scale + u_vertex_position, 0, 1);',
          `highp float yzoom = u_scale.y * ${this.drawingBufferHeight.toFixed(1)};
  highp float low = u_note.y;
  highp float high = u_note.y;
  if (u_conn_mode != 1 && u_next_note.x != 0.0) {
    low = min(low, u_next_note.y);
    high = max(high, u_next_note.y);
  }
  if (u_conn_mode == 4 && u_next_note.x != 0.0) {
    // bend extrapolates past the next pitch when the notes overlap
    highp float dx = u_next_note.x - u_note.x;
    highp float k = dx > 0.0 ? max(1.0, u_note.z / dx) : 1e6;
    highp float far = u_note.y + (u_next_note.y - u_note.y) * k;
    low = min(low, far);
    high = max(high, far);
  }
  highp float ext = u_size.x * (1.0 + abs(u_size.y)) + 1.0;
  highp vec2 pos = a_position * u_vertex_scale + u_vertex_position;
  // yzoom is negative in practice (load() receives pitchTop/pitchBottom
  // swapped), so order the bounds
  highp float y0 = (low - ext - u_offset.y) * 2.0 / yzoom - 1.0;
  highp float y1 = (high + ext - u_offset.y) * 2.0 / yzoom - 1.0;
  pos.y = clamp(pos.y, min(y0, y1), max(y0, y1));
  gl_Position = vec4(pos, 0, 1);`);
    }
    return shaderSource.call(this, shader, src);
  };

  let midi = null; // { notes, tempo, pitchTop, pitchBottom }
  let job = null;
  let main = null;
  let ctx = null;
  let panels = [];

  // split the notes into 4 voices by register (bass, tenor, alto, soprano)
  const registerVoice = pitch => {
    const p = 127 - pitch; // midiLoader stores pitches upside down
    if (p < 48) return 0;
    if (p < 60) return 1;
    if (p < 72) return 2;
    return 3;
  };

  // sync: { speed, offset, pins } maps MIDI time to a recording's time
  // (recording = speed * midi + offset) through the tempo map, like the
  // app's time syncher does; pins ([{ tick, recordingTime }]) bend that line
  // through notes placed by hand, as the sync desk does
  function loadMidi(base64, sync) {
    const file = MidiParser.parse(base64);
    midiLoader(file);
    const { notes, props } = loadedMidi;
    let { tempo } = loadedMidi;
    if (sync) {
      tempo = tempo.map(c => ({ ...c, real: sync.offset + sync.speed * c.real }));
      const pins = (sync.pins || []).slice().sort((a, b) => a.tick - b.tick);
      if (pins.length) {
        // before the first pin and after the last, keep the measured speed
        const real = tick => getRealFromMidi(tempo, tick);
        const first = pins[0], last = pins[pins.length - 1];
        const end = Math.max(...notes.map(n => n.start + n.length)) + 2000;
        tempo = [
          { midi: 0, real: first.recordingTime - (real(first.tick) - real(0)) },
          ...pins.map(p => ({ midi: p.tick, real: p.recordingTime })),
          { midi: end, real: last.recordingTime + (real(end) - real(last.tick)) },
        ].filter((c, i, all) => i === 0 || c.midi > all[i - 1].midi).map((c, id) => ({ ...c, id }));
      }
    }
    notes.forEach(n => { n.voice = registerVoice(n.pitch); });
    const end = Math.max(...notes.map(n =>
      getRealFromMidi(tempo, n.start + n.length)));
    midi = { notes, tempo, pitchTop: props.pitchTop,
      pitchBottom: props.pitchBottom, end };
    return { count: notes.length, end, pitchTop: props.pitchTop,
      pitchBottom: props.pitchBottom, tempo };
  }

  // brush assignment: 'all' -> first brush, [{ below: midiPitch, brush }],
  // or { hands: { "<tick>:<midi>": 'L' | 'R' }, L: brush(es), R: brush(es) },
  // which also makes each hand one voice so connections follow the hand; a
  // list of brushes draws the hand's notes once per brush, as layers
  const assignNotes = (scene) => {
    const ids = scene.brushes.map(b => b.id);
    return midi.notes.flatMap(n => {
      let brush = ids[0];
      if (scene.assign && scene.assign.hands) {
        const hand = scene.assign.hands[`${n.start}:${127 - n.pitch}`] || 'R';
        return [].concat(scene.assign[hand]).map(b => ({ ...n, brush: b, voice: hand === 'L' ? 0 : 1 }));
      }
      if (Array.isArray(scene.assign)) {
        const p = 127 - n.pitch;
        const rule = scene.assign.find(r => r.below === undefined || p < r.below);
        brush = rule.brush;
      }
      return { ...n, brush };
    });
  };

  function setupJob(j) {
    job = j;
    document.body.innerHTML = '';
    main = document.createElement('canvas');
    main.width = j.width;
    main.height = j.height;
    document.body.appendChild(main);
    ctx = main.getContext('2d');

    panels = j.panels.map(p => {
      const canv = document.createElement('canvas');
      canv.width = p.w;
      canv.height = p.h;
      return { ...p, canv, gl: renderer(canv), loaded: -1 };
    });
    return true;
  }

  const pieceTime = v => {
    if (job.loop) return job.pieceStart + (v % job.loop);
    return job.pieceStart + v;
  };

  function loadScene(panel, index) {
    const scene = panel.segments[index].scene;
    panel.gl.load(
      scene.brushes,
      scene.voices.map(c => ({ voiceColor: c })),
      assignNotes(scene),
      midi.tempo,
      scene.background,
      scene.pitchTop !== undefined ? scene.pitchTop : midi.pitchTop,
      scene.pitchBottom !== undefined ? scene.pitchBottom : midi.pitchBottom,
      scene.timeSpan,
      scene.playLine,
    );
    panel.loaded = index;
  }

  function label(text, x, y, size, align) {
    ctx.font = `600 ${size}px Inter, "DejaVu Sans", sans-serif`;
    ctx.textAlign = align || 'left';
    ctx.textBaseline = 'top';
    const w = ctx.measureText(text).width;
    const pad = size * 0.45;
    const bx = align === 'center' ? x - w / 2 - pad : x - pad;
    ctx.fillStyle = 'rgba(0,0,0,0.55)';
    ctx.fillRect(bx, y - pad * 0.6, w + pad * 2, size + pad * 1.2);
    ctx.fillStyle = '#fff';
    ctx.fillText(text, x, y);
  }

  function drawFrame(frame) {
    const v = frame / job.fps;
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, job.width, job.height);

    panels.forEach(panel => {
      let index = panel.segments.findIndex(s => v < s.until);
      if (index === -1) index = panel.segments.length - 1;
      if (index !== panel.loaded) loadScene(panel, index);

      panel.gl.render(pieceTime(v));
      ctx.drawImage(panel.canv, panel.x, panel.y);

      const text = panel.segments[index].label;
      if (text) {
        const size = panel.labelSize || Math.max(13, Math.round(panel.h / 22));
        label(text, panel.x + size * 0.8, panel.y + size * 0.7, size);
      }
      const sub = panel.segments[index].sublabel;
      if (sub) {
        const size = Math.round((panel.labelSize || panel.h / 22) * 0.7);
        label(sub, panel.x + size * 1.1, panel.y + size * 3.3, size);
      }
    });

    if (job.title) {
      const size = Math.round(job.height / 34);
      label(job.title, job.width / 2, job.height - size * 1.9, size, 'center');
    }
  }

  async function renderFrames(from, to) {
    for (let f = from; f < to; f++) {
      drawFrame(f);
      // JPEG keeps the upload small; raw RGBA readback + upload is ~10x slower
      const jpeg = await new Promise(r => main.toBlob(r, 'image/jpeg', job.quality));
      const res = await fetch('/frame', { method: 'POST', body: jpeg });
      if (!res.ok) throw new Error('frame upload failed: ' + res.status);
    }
    return to;
  }

  function destroy() {
    panels.forEach(p => {
      p.gl.destroy();
      const ext = p.canv.getContext('webgl').getExtension('WEBGL_lose_context');
      if (ext) ext.loseContext();
    });
    panels = [];
  }

  // FNV-1a hash of a rendered frame, used by verify.js
  function checksum(frame) {
    drawFrame(frame);
    const d = ctx.getImageData(0, 0, job.width, job.height).data;
    let h = 0x811c9dc5, lit = 0;
    for (let i = 0; i < d.length; i++) {
      h = Math.imul(h ^ d[i], 16777619);
      if ((i & 3) === 0 && d[i] > 40) lit++;
    }
    return [h >>> 0, lit];
  }

  function pixels(frame) {
    drawFrame(frame);
    return Array.from(ctx.getImageData(0, 0, job.width, job.height).data);
  }

  function glInfo() {
    const gl = document.createElement('canvas').getContext('webgl');
    if (!gl) return 'unavailable';
    const ext = gl.getExtension('WEBGL_debug_renderer_info');
    return gl.getParameter(ext ? ext.UNMASKED_RENDERER_WEBGL : gl.RENDERER);
  }

  return { loadMidi, setupJob, glInfo, renderFrames, destroy, checksum, pixels,
    defaults: () => ({ ...brushTemplate }) };
})();
