# Offline video renderer

Renders MuVis animations of a MIDI file to MP4 (with audio), using the app's
own `midiLoader.js` and WebGL renderer (`renderer/`) in headless Chromium.

## Quick start

```
git clone -b claude/eager-cori-sjugt8 https://github.com/ysetbon/midianimation.git && cd midianimation/tools/video-render && npm install && npx playwright install chromium && node render.js /path/to/file.mid out
```

Videos land in `out/`. To render only some of them, list job names after
the output folder (see *Jobs* below).

Requirements: Node 18+, `ffmpeg`, and optionally `fluidsynth` with a General
MIDI soundfont for audio (set `SOUNDFONT=/path/to/file.sf2` if it is not in a
standard location; without one the videos are silent).

- Debian/Ubuntu: `sudo apt-get install ffmpeg fluidsynth fluid-soundfont-gm`
- macOS: `brew install ffmpeg fluid-synth`, plus a `.sf2` soundfont
- Windows: `winget install ffmpeg`, plus FluidSynth and a `.sf2` soundfont

The renderer uses the GPU when Chromium can get one, and prints the WebGL
renderer it ended up with. If it reports SwiftShader or llvmpipe, try
`HEADED=1` (opens a browser window, which some drivers need). `GL=cpu`
forces software rendering.

`START_SECONDS` / `MAX_SECONDS` render only part of each job, which is handy
for previews. Several workers can run at once on different jobs; to see
progress bars and a time estimate for all of them:

```
node tools/video-render/progress.js <outdir>
```

## Jobs

Defined in `jobs.js`. Together they cover every option a brush offers:

| Job | What it shows |
| --- | --- |
| `01_showcase_all_options` | The whole piece at 1080p, stepping through every option one at a time, with captions |
| `02_grid_shape_x_playmode` | 4×4 grid: every shape × every play mode |
| `03_grid_shape_x_connect` | 4×4 grid: every shape × every connect mode |
| `04_grid_colour_and_effects` | 3×3 grid: colour modes, size curve, time curve, time zoom, appear back, layered brushes |
| `05_preset_tristan`, `06_preset_kyrie`, `07_preset_rameau` | The brushes of the three example projects in `states/`, applied to the MIDI |
| `08a`–`08d_catalog_<shape>` | Every play mode × connect mode × colour mode for each shape (192 combinations in all), 3 seconds each |

Notes are split into 4 voices by register (bass < C3, tenor < C4, alto < C5,
soprano) so that the *voice* colour mode and the connect modes have melodic
lines to work with. The *line* connect mode has no visual effect in the
current shader, so it renders like *none*.

## Speed

Without a GPU, Chromium falls back to SwiftShader. The repo's vertex shader
draws each note as a square quad, so most shaded fragments are empty; the
harness patches the vertex shader (only inside the harness) to clamp each
quad vertically to the pitch range the note can reach. `verify.js` checks
that this produces pixel-identical frames for every scene:

```
node tools/video-render/verify.js <file.mid> [job names...]
```
