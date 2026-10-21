# Offline video renderer

Renders MuVis animations of a MIDI file to MP4 (with audio), using the app's
own `midiLoader.js` and WebGL renderer (`renderer/`) in headless Chromium.

```
node tools/video-render/render.js <file.mid> <outdir> [job names...]
```

Requirements: Node with [Playwright](https://playwright.dev) (Chromium),
`ffmpeg`, and `fluidsynth` with a General MIDI soundfont
(`/usr/share/sounds/sf2/FluidR3_GM.sf2` by default, override with `SOUNDFONT`).
On Debian/Ubuntu: `apt-get install ffmpeg fluidsynth fluid-soundfont-gm`.

`START_SECONDS` / `MAX_SECONDS` render only part of each job, which is handy
for previews.

## Jobs

Defined in `jobs.js`. Together they cover every option a brush offers:

| Job | What it shows |
| --- | --- |
| `01_showcase_all_options` | The whole piece at 1080p, stepping through every option one at a time, with captions |
| `02_grid_shape_x_playmode` | 4×4 grid: every shape × every play mode |
| `03_grid_shape_x_connect` | 4×4 grid: every shape × every connect mode |
| `04_grid_colour_and_effects` | 3×3 grid: colour modes, size curve, time curve, time zoom, appear back, layered brushes |
| `05_preset_tristan`, `06_preset_kyrie`, `07_preset_rameau` | The brushes of the three example projects in `states/`, applied to the MIDI |
| `08_catalog_all_192_combinations` | Every shape × play mode × connect mode × colour mode, 3 seconds each |

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
node tools/video-render/verify.js <file.mid>
```
