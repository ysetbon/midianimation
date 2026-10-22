const renderer = canv => {
  'use strict';

  const source = `// vertex shader
#line 6

precision lowp float;

attribute vec2 a_position;

uniform vec2 u_vertex_position;
uniform float u_vertex_scale;

uniform vec2 u_scale;
uniform vec2 u_offset;

uniform vec2 u_curve;

uniform float u_time; // current time
uniform vec3 u_note; // x: start, y: pitch, z: length
uniform vec2 u_size; // x: size, y: size curve

varying float v_size;
varying float v_inv_size;

void main() {
  v_size = u_size.x;
  if (u_time > u_note.x && u_time < u_note.x + u_note.z)
    v_size *= 1.0 + u_size.y * pow(1.0 - (u_time - u_note.x) / u_note.z, 0.5);

  v_inv_size = 1.0 / (v_size * 0.5);

  gl_Position = vec4(a_position * u_vertex_scale + u_vertex_position, 0, 1);
}`; // end of vertex shader

  const attributes = {preserveDrawingBuffer: true};
  const gl = canv.getContext('webgl', attributes) ||
    canv.getContext('experimental-webgl', attributes); // TODO message if failed
  
  var brushes = [];

  const shader = gl.createShader(gl.VERTEX_SHADER);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  console.log(gl.getShaderInfoLog(shader));

  const normalBrush = NormalBrush(gl, shader);

  gl.enable(gl.BLEND);
  gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

  gl.viewport(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight);

  // playLine: where notes are played, as a fraction of the screen width
  function load(newBrushes, voices, notes, tempo, background, pitchBottom, pitchTop, timeSpan, playLine = 0.5) {
    gl.clearColor(...background, 1.0);

    brushes = [];
    notes = notes.sort((a, b) => a.start - b.start);

    newBrushes.forEach(b => {
      const brush = {
        notes: [],
        xzoom: timeSpan / b.timeZoom,
        yzoom: pitchBottom - pitchTop,
        yoffset: pitchTop - 0.5,
        xoffset: -playLine * timeSpan / b.timeZoom, // the play line at playLine of the width
        shape: b.shape,
        playMode: b.playMode,
        size: [b.size, b.sizeCurve],
        timeCurve1: b.timeCurve1,
        timeCurve2: 1.0 / b.timeCurve2,
        connectMode: b.connectMode,
        appearBack: b.appearBack,
        vanish: b.vanish || brushVanishModes.NEVER,
        // morph: notes struck between morphStart and morphEnd (seconds) turn
        // gradually into morphShape, with its size and colours
        morph: b.morphShape && b.morphShape !== '0' ? {
          shape: b.morphShape,
          start: b.morphStart || 0,
          end: b.morphEnd || 0,
          size: [b.morphSize !== undefined ? b.morphSize : b.size,
            b.morphSizeCurve !== undefined ? b.morphSizeCurve : b.sizeCurve],
          leftColor: b.morphLeftColor,
          rightColor: b.morphRightColor,
        } : null,
        // jump: struck notes leap jumpHeight pitch steps and land after
        // jumpLength seconds; jumpVelocity (0-1) makes loud notes leap higher
        jump: b.jumpHeight > 0 ? {
          height: b.jumpHeight,
          length: b.jumpLength || 0.4,
          velocity: b.jumpVelocity !== undefined ? b.jumpVelocity : 0.5,
        } : null,
        // TODO other properties
      };
      const morphOf = realStart => {
        const m = brush.morph;
        const t = m.end > m.start ? (realStart - m.start) / (m.end - m.start) : realStart >= m.start ? 1 : 0;
        const c = Math.min(1, Math.max(0, t));
        return c * c * (3 - 2 * c); // ease in and out
      };
      const mixColor = (a, b, t) => b ? a.map((v, i) => v + (b[i] - v) * t) : a;

      let colorFunc;
      switch(b.colorMode) {
        case brushColorModes.VOICE:
          colorFunc = (n) => [voices[n.voice].voiceColor, [1,1,1]];
          break;
        case brushColorModes.PITCH:
          colorFunc = (n) => [
            [[1,0,0], [1,1,1]],
            [[.75,0,.25], [1,1,1]],
            [[.5,0,.5], [1,1,1]],
            [[.25,0,.75], [1,1,1]],
            [[0,0,1], [1,1,1]],
            [[0,.5,.5], [1,1,1]],
            [[0,1,0], [1,1,1]],
            [[.25,.75,0], [1,1,1]],
            [[.5,.5,0], [1,1,1]],
            [[.625,.375,0], [1,1,1]],
            [[.75,.25,0], [1,1,1]],
            [[.875,.125,0], [1,1,1]],
          ][(n.pitch * 7) % 12];
          break;
        case brushColorModes.UNIFORM:
        default:
          colorFunc = () => [b.leftColor, b.rightColor];
      }

      const lastNotePerVoice = new Array(voices.length);

      const inv_xzoom = 2.0 / brush.xzoom;
      const inv_yzoom = 2.0 / brush.yzoom;
      const max_ysize = Math.max(brush.size[0] * (1.0 + brush.size[1]),
        brush.morph ? brush.morph.size[0] * (1.0 + brush.morph.size[1]) : 0);

      notes.forEach(n => { // TODO: loop over notes only once 
        if (n.brush === b.id) {
          const colors = colorFunc(n);
          const realStart = getRealFromMidi(tempo, n.start);
          const realLength = getRealFromMidi(tempo, n.start + n.length) - realStart;
          
          const note = {
            pitch: n.pitch,
            start: realStart,
            length: realLength,
            next: null,
            color1: colors[0],
            color2: colors[1],
            velocity: n.velocity !== undefined ? n.velocity : 90,
            morph: 0,
            size: brush.size,
            vertexPosition: [
              (realStart + realLength * 0.5) * inv_xzoom,
              (n.pitch - brush.yoffset) * inv_yzoom,
            ],
            vertexScale: (realLength + brush.timeCurve1) * inv_xzoom - inv_yzoom * max_ysize,
            vertexPositionPlaying: [0, 0],
            vertexScalePlaying: 0,
          };

          if (brush.morph) {
            const m = note.morph = morphOf(realStart);
            note.color1 = mixColor(note.color1, brush.morph.leftColor, m);
            note.color2 = mixColor(note.color2, brush.morph.rightColor, m);
            note.size = brush.size.map((v, i) => v + (brush.morph.size[i] - v) * m);
          }

          const last = lastNotePerVoice[n.voice];
          if (brush.connectMode !== brushConnectModes.NONE &&
            last &&
            (note.start - (last.start + last.length)) < b.connectDistance)
          {
            last.next = note;
            const length = note.start + note.length - last.start;
            const pitch = (note.pitch + last.pitch) * 0.5
            last.vertexPositionPlaying = [
              (last.start + length * 0.5) * inv_xzoom,
              (pitch - brush.yoffset) * inv_yzoom,
            ];
            last.vertexScalePlaying = Math.max(
              (length + brush.timeCurve1) * inv_xzoom,
              Math.abs(note.pitch - last.pitch) * -inv_yzoom * max_ysize,
            );
          }
          lastNotePerVoice[n.voice] = note;

          brush.notes.push(note);
        }
      });

      brushes.push(brush);
    });
  };

  function render(time) {
    gl.viewport(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight);
    gl.clear(gl.COLOR_BUFFER_BIT);

    brushes.forEach(b => {
      normalBrush.render(b, b.notes, time);
    });
  };

  function destroy() {
    normalBrush.destroy();
    gl.deleteShader(shader);
  }

  return {
    load,
    render,
    destroy,
  };
};