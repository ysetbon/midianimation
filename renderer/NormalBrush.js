const NormalBrush = (gl, vertexShader) => {
  'use strict';

  const source = `// GLSL fragment shader
#line 6

#define M_PI 3.1415926535897932384626433832795
#define FALSE 0
#define TRUE 1

#define SHAPE_RECT 1
#define SHAPE_CIRCLE 2
#define SHAPE_TRIANGLE 3
#define SHAPE_BLOB 4
#define SHAPE_DIAMOND 5
#define SHAPE_RING 6
#define SHAPE_STAR 7 // four-pointed

#define PLAY_MASK 1 // color changes at current point
#define PLAY_FLIP 2 // whole note flips color at once
#define PLAY_ON_OFF 3 // flips color when played and flip back
#define PLAY_FLASH 4 // flip color and slowly change back

#define CONN_NONE 1
#define CONN_LINE 2 // connect through a line
#define CONN_FLOAT 3 // float whole note towards next note
#define CONN_BEND 4

#define VANISH_NEVER 0
#define VANISH_RELEASED 1 // disappear the moment the note ends
#define VANISH_STRUCK 2 // fade out as soon as the note is struck
#define VANISH_FADE 0.1 // seconds, for VANISH_STRUCK

precision lowp float;

uniform int u_shape;
uniform int u_shape2; // shape to morph into, 0 for none
uniform float u_morph; // 0: u_shape, 1: u_shape2, in between: a blend of the two
uniform vec3 u_motion; // x: shift in seconds, y: horizontal scale, z: opacity
uniform int u_play_mode;
uniform int u_conn_mode;
uniform int u_appear_back;
uniform int u_vanish;

uniform vec2 u_scale;
uniform vec2 u_offset;

uniform float u_time; // current time
uniform vec2 u_curve; // time curvature

uniform vec3 u_note; // x: start, y: pitch, z: length
uniform vec2 u_size; // x: size, y: size curve
uniform vec3 u_next_note;

uniform vec3 u_color1;
uniform vec3 u_color2;

varying float v_size;
varying float v_inv_size;

float rect(const vec2 coord, const vec3 note, const float size) {
  if (coord.x < note.x || coord.x > note.x + note.z ||
    coord.y < note.y - size * 0.5 || coord.y > note.y + size * 0.5)
  {
    return 0.0;
  }
  return 1.0;
}

bool rectb(const vec2 coord, const vec3 note, const float size) {
  return !(coord.x < note.x || coord.x > note.x + note.z ||
    coord.y < note.y - size * 0.5 || coord.y > note.y + size * 0.5);
}

float triangle(const vec2 coord, const vec3 note, const float size) {
  if (!rectb(coord, note, size)) return 0.0;
  float width = (1.0 - (coord.x - note.x) / note.z) * size * 0.5;
  return clamp((width - abs(coord.y - note.y)) * 10.0, 0.0, 1.0);
}

float circle(const vec2 coord, const vec3 note, const float size) {
  if (!rectb(coord, note, size)) return 0.0;
  float center = note.x + note.z * 0.5;
  float x = (coord.x - center) / (note.z * 0.5);
  float y = (coord.y - note.y) / (size * 0.5);
  float dist = length(vec2(x, y));
  return clamp((1.0 - dist) * 10.0, 0.0, 1.0);
}

float blob(const vec2 coord, const vec3 note, const float size) {
  if (!rectb(coord, note, size)) return 0.0;
  float center = note.x + note.z * 0.5;
  float x = (coord.x - center) / (note.z * 0.5);
  float y = (coord.y - note.y) / (size * 0.5);
  float dist = length(vec2(x, y));
  return clamp((1.0 - dist), 0.0, 1.0);
}

// how far inside the shape a point is: 0 on the outline, negative outside;
// shapes are blended by mixing these
float field(const int shape, const vec2 coord, const vec3 note, const float size) {
  float x = (coord.x - note.x - note.z * 0.5) / (note.z * 0.5);
  float y = (coord.y - note.y) / (size * 0.5);
  if (abs(x) > 1.0 || abs(y) > 1.0) return -1.0;
  if (shape == SHAPE_RECT) return min(1.0 - abs(x), 1.0 - abs(y));
  if (shape == SHAPE_TRIANGLE) return (1.0 - x) * 0.5 - abs(y);
  if (shape == SHAPE_DIAMOND) return 1.0 - abs(x) - abs(y);
  if (shape == SHAPE_RING) return 0.22 - abs(length(vec2(x, y)) - 0.75);
  if (shape == SHAPE_STAR) return 1.0 - pow(sqrt(abs(x)) + sqrt(abs(y)), 2.0);
  return 1.0 - length(vec2(x, y)); // circle, blob
}

float sharpness(const int shape) {
  return shape == SHAPE_BLOB ? 1.0 : 10.0;
}

float diamond(const vec2 coord, const vec3 note, const float size) {
  return clamp(field(SHAPE_DIAMOND, coord, note, size) * 10.0, 0.0, 1.0);
}

float ring(const vec2 coord, const vec3 note, const float size) {
  return clamp(field(SHAPE_RING, coord, note, size) * 10.0, 0.0, 1.0);
}

float star(const vec2 coord, const vec3 note, const float size) {
  return clamp(field(SHAPE_STAR, coord, note, size) * 10.0, 0.0, 1.0);
}

float morphed(const vec2 coord, const vec3 note, const float size) {
  float f = mix(field(u_shape, coord, note, size), field(u_shape2, coord, note, size), u_morph);
  return clamp(f * mix(sharpness(u_shape), sharpness(u_shape2), u_morph), 0.0, 1.0);
}

void main() {
  vec2 coord = (gl_FragCoord.xy * u_scale) + u_offset;

  if (u_curve.y != 1.0) {
    coord.x -= u_time;
    coord.x /= u_curve.x;

    if (coord.x <= -1.0) {
      coord.x += 1.0 - u_curve.y;
    } else if (coord.x < 1.0) {
      coord.x *= u_curve.y; // += cos
    } else {
      coord.x -= 1.0 - u_curve.y;
    }

    coord.x *= u_curve.x;
    coord.x += u_time;
  }

  if (u_motion.x != 0.0 || u_motion.y != 1.0) {
    float centre = u_note.x + u_note.z * 0.5;
    coord.x = centre + (coord.x - centre - u_motion.x) / u_motion.y;
  }

  vec3 note = u_note;

  float opacity = 1.0;

  if (u_next_note.x != 0.0) {
    if (u_conn_mode == CONN_LINE) {

    } else if (u_conn_mode == CONN_BEND) {
      if (coord.x > note.x)
        note.y += (u_next_note.y - note.y) * (coord.x - note.x) / (u_next_note.x - note.x);
    } else if (u_conn_mode == CONN_FLOAT) {
      if (u_time > u_next_note.x) {
        if (u_appear_back == FALSE) {
          gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
          return;
        }
      } else if (u_time > note.x) {
        float transition = (u_time  - note.x) / (u_next_note.x - note.x);
        note.x += (u_next_note.x - note.x) * transition;
        note.y += (u_next_note.y - note.y) * pow(transition, 1.5);
        note.z += (u_next_note.z - note.z) * transition;
        opacity = 1.0 - pow(transition, 2.0);
      }
    }
  }

  #define RENDER(func) {` +
    `val = func(coord, note, v_size) * opacity;` +
    `if (u_appear_back == TRUE) {` +
      `val = max(val, func(coord, u_note, u_size.x) * (1.0 - opacity));` +
    `}` +
  `}

  float val;
  int shape = u_shape2 > 0 && u_morph >= 1.0 ? u_shape2 : u_shape;

  if (u_shape2 > 0 && u_morph > 0.0 && u_morph < 1.0) RENDER(morphed)
  else if (shape == SHAPE_RECT) RENDER(rect)
  else if (shape == SHAPE_TRIANGLE) RENDER(triangle)
  else if (shape == SHAPE_CIRCLE) RENDER(circle)
  else if (shape == SHAPE_BLOB) RENDER(blob)
  else if (shape == SHAPE_DIAMOND) RENDER(diamond)
  else if (shape == SHAPE_RING) RENDER(ring)
  else if (shape == SHAPE_STAR) RENDER(star)
  else return;

  if (u_vanish == VANISH_RELEASED && u_time >= u_note.x + u_note.z) {
    val = 0.0; // gone exactly when the note ends
  } else if (u_vanish == VANISH_STRUCK && u_time > u_note.x) {
    val *= clamp(1.0 - (u_time - u_note.x) / VANISH_FADE, 0.0, 1.0);
  }

  val *= u_motion.z;

  if (val == 0.0) {
    gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
    return;
  }

  vec3 color;

  if (u_play_mode == PLAY_MASK) {
    if (coord.x - (note.x - u_note.x) > u_time)
      color = u_color1;
    else
      color = u_color2;
  } else if (u_play_mode == PLAY_FLIP) {
    if (u_note.x > u_time)
      color = u_color1;
    else
      color = u_color2;
  } else if (u_play_mode == PLAY_ON_OFF) {
    if (u_note.x  > u_time || u_note.x + u_note.z < u_time)
      color = u_color1;
    else
      color = u_color2;
  } else if (u_play_mode == PLAY_FLASH) {
    if (u_note.x  > u_time || u_note.x + u_note.z < u_time)
      color = u_color1;
    else
      color = mix(u_color2, u_color1, (u_time - u_note.x) / u_note.z);
  } else {
    color = u_color1;
  }

  gl_FragColor = vec4(color, val);
}`; // end of GLSL shader

  const shader = gl.createShader(gl.FRAGMENT_SHADER);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  console.log(gl.getShaderInfoLog(shader));

  const prog = gl.createProgram();
  gl.attachShader(prog, shader);
  gl.attachShader(prog, vertexShader);
  gl.linkProgram(prog);
  console.log(gl.getProgramInfoLog(prog));
  gl.useProgram(prog);

  const a_position = gl.getAttribLocation(prog, 'a_position');

  const u = name => gl.getUniformLocation(prog, name),
    u_vertexPosition = u('u_vertex_position'),
    u_vertexScale = u('u_vertex_scale'),
    u_playMode = u('u_play_mode'),
    u_shape = u('u_shape'),
    u_shape2 = u('u_shape2'),
    u_morph = u('u_morph'),
    u_motion = u('u_motion'),
    u_connMode = u('u_conn_mode'),
    u_appearBack = u('u_appear_back'),
    u_vanish = u('u_vanish'),
    u_scale = u('u_scale'),
    u_offset = u('u_offset'),
    u_time = u('u_time'),
    u_curve = u('u_curve'),
    u_note = u('u_note'),
    u_size = u('u_size'),
    u_nextNote = u('u_next_note'),
    u_color1 = u('u_color1'),
    u_color2 = u('u_color2');

  const square = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, square);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
    -1.0,-1.0, 1.0,-1.0, -1.0,1.0,
    -1.0,1.0 ,1.0,-1.0, 1.0,1.0,
  ]), gl.STATIC_DRAW);

  // effects drawn around a struck note (ripple, echo, burst), in pixels
  const effectVertex = `// effect vertex shader
attribute vec2 a_position;
uniform vec2 u_centre;
uniform vec2 u_half;
void main() {
  gl_Position = vec4(u_centre + a_position * u_half, 0, 1);
}`;
  const effectFragment = `// effect fragment shader
precision highp float;
#define SHAPE_RECT 1
#define SHAPE_TRIANGLE 3
#define SHAPE_STAR 7
uniform int u_kind; // 1 ripple, 2 echo, 3 burst
uniform vec2 u_px; // where the note was struck, in pixels
uniform vec2 u_note_half; // the note's half width and height, in pixels
uniform float u_u; // 0 at the strike, 1 when the effect is over
uniform float u_k; // strength, after velocity and weight
uniform float u_w; // weight
uniform float u_unit; // pixels per sketch pixel (screen height / 680)
uniform float u_height; // screen height in pixels
uniform vec3 u_color;
uniform int u_shape;
uniform int u_shape2;
uniform float u_morph;
uniform float u_seed;
uniform float u_jit[9];

float easeOut(float t) { float c = 1.0 - clamp(t, 0.0, 1.0); return 1.0 - c * c * c; }

float field(int shape, vec2 p) {
  if (shape == SHAPE_RECT) return min(1.0 - abs(p.x), 1.0 - abs(p.y));
  if (shape == SHAPE_TRIANGLE) return (1.0 - p.x) * 0.5 - abs(p.y);
  if (shape == SHAPE_STAR) return 1.0 - pow(sqrt(abs(p.x)) + sqrt(abs(p.y)), 2.0);
  return 1.0 - length(p);
}

void main() {
  vec2 frag = gl_FragCoord.xy;
  float u = u_u, fade = min(1.0, u_w * 1.5), a = 0.0;
  if (u_kind == 1) {
    float r = 4.0 * u_unit + u_k * u_height * 0.13 * easeOut(u);
    float lw = (0.6 + 2.4 * (1.0 - u)) * u_unit;
    a = 0.85 * (1.0 - u) * fade * clamp(lw * 0.5 + 0.5 - abs(length(frag - u_px) - r), 0.0, 1.0);
  } else if (u_kind == 2) {
    float s = 1.0 + u_k * 1.8 * easeOut(u);
    vec2 extent = vec2(u_note_half.x * s + 3.0 * s * u_unit, u_note_half.y * s);
    vec2 p = (frag - u_px) / extent;
    float f = mix(field(u_shape, p), field(u_shape2, p), u_morph);
    a = 0.8 * (1.0 - u) * fade * clamp(0.6 * u_unit + 0.5 - abs(f) * min(extent.x, extent.y), 0.0, 1.0);
  } else {
    float r = (0.8 + 2.4 * (1.0 - u)) * u_unit;
    for (int j = 0; j < 9; j++) {
      float ang = (float(j) / 9.0 + u_seed) * 6.2831853;
      float d = u_k * u_height * 0.11 * easeOut(u) * u_jit[j];
      vec2 p = u_px + vec2(cos(ang), -sin(ang)) * d - vec2(0.0, u_height * 0.08 * u * u);
      a = max(a, clamp(r + 0.5 - length(frag - p), 0.0, 1.0));
    }
    a *= (1.0 - u) * fade;
  }
  if (a <= 0.0) discard;
  gl_FragColor = vec4(u_color, a);
}`;
  const compile = (type, src) => { const sh = gl.createShader(type); gl.shaderSource(sh, src); gl.compileShader(sh); return sh; };
  const effectShaders = [compile(gl.VERTEX_SHADER, effectVertex), compile(gl.FRAGMENT_SHADER, effectFragment)];
  const effectProg = gl.createProgram();
  effectShaders.forEach(sh => gl.attachShader(effectProg, sh));
  gl.linkProgram(effectProg);
  console.log(gl.getProgramInfoLog(effectProg));
  const e = name => gl.getUniformLocation(effectProg, name);
  const eu = {}; ['u_centre', 'u_half', 'u_kind', 'u_px', 'u_note_half', 'u_u', 'u_k', 'u_w', 'u_unit',
    'u_height', 'u_color', 'u_shape', 'u_shape2', 'u_morph', 'u_seed', 'u_jit'].forEach(n => { eu[n] = e(n); });
  const e_position = gl.getAttribLocation(effectProg, 'a_position');
  const EFFECTS = { ripple: 1, echo: 2, burst: 3 };
  const hash = i => { const s = Math.sin(i * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
  const smoothstep = t => { const c = Math.min(1, Math.max(0, t)); return c * c * (3 - 2 * c); };

  function drawEffects(effects) {
    if (!effects.length) return;
    const W = gl.drawingBufferWidth, H = gl.drawingBufferHeight, unit = H / 680;
    gl.useProgram(effectProg);
    gl.bindBuffer(gl.ARRAY_BUFFER, square);
    gl.enableVertexAttribArray(e_position);
    gl.vertexAttribPointer(e_position, 2, gl.FLOAT, false, 0, 0);
    gl.uniform1f(eu.u_unit, unit);
    gl.uniform1f(eu.u_height, H);
    effects.forEach(f => {
      const kind = EFFECTS[f.type], u = f.u, k = f.k;
      let half;
      if (kind === 1) half = [4 * unit + k * H * 0.13 + 3 * unit + 2, 0];
      else if (kind === 2) { const s = 1 + k * 1.8; half = [f.hw * s + 3 * s * unit + 2, f.hh * s + 2]; }
      else half = [k * H * 0.11 + H * 0.08 + 4 * unit + 2, 0];
      if (!half[1]) half[1] = half[0];
      gl.uniform2f(eu.u_centre, f.px[0] / W * 2 - 1, f.px[1] / H * 2 - 1);
      gl.uniform2f(eu.u_half, half[0] / W * 2, half[1] / H * 2);
      gl.uniform1i(eu.u_kind, kind);
      gl.uniform2f(eu.u_px, f.px[0], f.px[1]);
      gl.uniform2f(eu.u_note_half, f.hw, f.hh);
      gl.uniform1f(eu.u_u, u); gl.uniform1f(eu.u_k, k); gl.uniform1f(eu.u_w, f.w);
      gl.uniform3f(eu.u_color, ...(kind === 2 ? f.note.color1 : f.note.color2));
      gl.uniform1i(eu.u_shape, f.shape); gl.uniform1i(eu.u_shape2, f.shape2 || f.shape); gl.uniform1f(eu.u_morph, f.morph);
      gl.uniform1f(eu.u_seed, hash(f.note.id));
      gl.uniform1fv(eu.u_jit, Array.from({ length: 9 }, (_, j) => 0.6 + 0.4 * hash(f.note.id * 9 + j)));
      gl.drawArrays(gl.TRIANGLES, 0, 6);
    });
  }

  function render(brush, notes, time) {
    gl.useProgram(prog);

    gl.uniform2f(u_scale, brush.xzoom / gl.drawingBufferWidth,
      brush.yzoom / gl.drawingBufferHeight);
    gl.uniform2f(u_offset, brush.xoffset + time, brush.yoffset);
    gl.uniform1f(u_time, time);

    gl.uniform2f(u_size, ...brush.size);
    gl.uniform1i(u_playMode, brush.playMode);
    gl.uniform1i(u_shape, brush.shape);
    gl.uniform1i(u_shape2, brush.morph ? brush.morph.shape : 0);
    gl.uniform1f(u_morph, 0.0);
    gl.uniform3f(u_motion, 0.0, 1.0, 1.0);
    gl.uniform1i(u_connMode, brush.connectMode);
    gl.uniform1i(u_appearBack, brush.appearBack);
    gl.uniform1i(u_vanish, brush.vanish);
    gl.uniform2f(u_curve, brush.timeCurve1, brush.timeCurve2);

    gl.enableVertexAttribArray(a_position);
    gl.vertexAttribPointer(a_position, 2, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ARRAY_BUFFER, square);

    const leftBound = brush.xoffset + time;
    const rightBound = brush.xoffset + time + brush.xzoom;

    const i = notes[Symbol.iterator]();
    let nxt;

    // iterate towards the first note in view
    for(nxt = i.next();
      nxt.done !== true && (
        nxt.value.next ?
          (nxt.value.next.start + nxt.value.next.length < leftBound) :
          (nxt.value.start + nxt.value.length < leftBound)
      ); nxt = i.next());
    
    const inv_xzoom = 2.0 / brush.xzoom;
    const inv_yzoom = 2.0 / brush.yzoom;

    // jump: a struck note leaps up (in pitch steps) and lands again
    const jump = brush.jump;
    const liftOf = note => {
      const u = (time - note.start) / jump.length;
      if (u < 0 || u >= 1) return 0;
      const force = 1 - jump.velocity + jump.velocity * Math.min(1.4, note.velocity / 90);
      return jump.height * force * Math.sin(Math.PI * u);
    };

    // motions: what a struck note does (rise, shake, squash, jump and the
    // effects around it), each weighted by when the note is struck
    const W_px = gl.drawingBufferWidth, H_px = gl.drawingBufferHeight;
    const steps = Math.abs(brush.yzoom); // pitch steps the screen height covers
    const effects = [];
    const motionOf = note => {
      const m = { lift: 0, dx: 0, sx: 1, sy: 1, alpha: 1 };
      const a = time - note.start;
      if (a < 0) return m;
      brush.motions.forEach((mo, j) => {
        const w = note.motionWeights[j];
        if (!w) return;
        const u = a / mo.length;
        const k = mo.strength * (1 - mo.velocity + mo.velocity * Math.min(1.4, note.velocity / 90)) * w;
        if (mo.type === 'jump') { if (u < 1) m.lift += k * Math.sin(Math.PI * u); }
        else if (mo.type === 'rise') {
          const c = Math.min(1, u); m.lift += k * 0.12 * steps * smoothstep(c); m.alpha *= 1 - 0.55 * c * w;
        } else if (mo.type === 'shake') {
          if (u < 1) {
            m.dx += k * 0.012 * H_px * Math.sin(a * 70) * (1 - u) / W_px * brush.xzoom;
            m.lift -= k * 0.007 * steps * Math.cos(a * 53) * (1 - u);
          }
        } else if (mo.type === 'squash') {
          if (u < 1) { const q = k * 0.55 * Math.exp(-5 * u) * Math.cos(10 * u); m.sx *= 1 + q; m.sy /= 1 + q; }
        } else if (EFFECTS[mo.type] && u < 1) {
          effects.push({ type: mo.type, u, k, w, note });
        }
      });
      return m;
    };

    for(;nxt.done !== true && nxt.value.start < rightBound;
      nxt = i.next())
    { // TODO: put whole note into one datastructure, at load()
      const note = nxt.value;
      const nextNote = note.next;
      const motion = brush.motions ? motionOf(note) : null;
      const lift = (jump ? liftOf(note) : 0) + (motion ? motion.lift : 0); // pitches are stored upside down
      const liftY = -lift * inv_yzoom;
      const shiftX = motion ? motion.dx * inv_xzoom : 0;
      const widen = motion ? Math.max(1, motion.sx) : 1;

      if (brush.connectMode !== brushConnectModes.NONE && nextNote &&
        time >= note.start && time <= nextNote.start + nextNote.length) {
        gl.uniform2f(u_vertexPosition,
          note.vertexPositionPlaying[0] - leftBound * inv_xzoom - 1.0,
          note.vertexPositionPlaying[1] + liftY - 1.0,
        );
        gl.uniform1f(u_vertexScale, note.vertexScalePlaying);
      } else {
        gl.uniform2f(u_vertexPosition,
          note.vertexPosition[0] + shiftX - leftBound * inv_xzoom - 1.0,
          note.vertexPosition[1] + liftY - 1.0,
        );
        gl.uniform1f(u_vertexScale, note.vertexScale * widen);
      }

      gl.uniform3f(u_note, note.start, note.pitch - lift, note.length);
      gl.uniform3f(u_color1, ...note.color1);
      gl.uniform3f(u_color2, ...note.color2);
      if (brush.morph) {
        gl.uniform1f(u_morph, note.morph);
        gl.uniform2f(u_size, ...note.size);
      }
      if (motion) {
        const size = brush.morph ? note.size : brush.size;
        gl.uniform2f(u_size, size[0] * motion.sy, size[1]);
        gl.uniform3f(u_motion, motion.dx, motion.sx, motion.alpha);
        // where effects start: the strike point, scrolling with the note
        effects.forEach(f => {
          if (f.note !== note || f.px) return;
          f.px = [((note.start - leftBound) * inv_xzoom) / 2 * W_px, note.vertexPosition[1] / 2 * H_px];
          f.hw = note.length / brush.xzoom * W_px / 2;
          f.hh = Math.max(2.2 * H_px / 680, (brush.morph ? note.size[0] : brush.size[0]) * 0.5 / steps * H_px);
          f.shape = Number(brush.shape); f.shape2 = brush.morph ? Number(brush.morph.shape) : 0; f.morph = note.morph || 0;
        });
      }
      if (brush.connectMode !== brushConnectModes.NONE) {
        if (nextNote)
          gl.uniform3f(u_nextNote, nextNote.start, nextNote.pitch, nextNote.length);
        else
          gl.uniform3f(u_nextNote, 0.0, 0.0, 0.0);
      }
      gl.drawArrays(gl.TRIANGLES, 0, 6);
    }
    drawEffects(effects);
  };

  function destroy() {
    gl.deleteProgram(prog);
    gl.deleteShader(shader);
    gl.deleteProgram(effectProg);
    effectShaders.forEach(sh => gl.deleteShader(sh));
    gl.deleteBuffer(square);
  }

  return { render, destroy };
};