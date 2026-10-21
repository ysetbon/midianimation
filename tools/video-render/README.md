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

| `10_hands_blocks` | Right hand as two layered brushes (a soft glow under triangles), left hand as blocks; notes vanish once struck and are played at 40% of the screen width. Only when a hand split exists |
| `09_layered_hands` | Layered brushes split by hand: right hand yellow triangles, left hand purple blobs. Only when a hand split exists (see below) |

## Using a recording

To put the original recording under the video instead of FluidSynth, pass it
in `AUDIO` and say how MIDI time maps to it in `AUDIO_SYNC`
(`<speed>:<offset>`: recording time = speed × MIDI time + offset). The video
then runs for the length of the recording. For `17_ethude1.mid` and its
recording `ethude1_2026(17).mp3`:

```
AUDIO="ethude1_2026(17).mp3" AUDIO_SYNC=1.0434:0.04 node tools/video-render/render.js 17_ethude1.mid out 10_hands_blocks
```

The sync was found by matching the recording's note onsets against the MIDI
notes: the MIDI file runs 4.3% faster than the recording, and with this sync
half of the notes land within 4 ms of their attack in the recording.

## Hand split

`hands.js` decides which hand plays each note by asking TypeSafe's Jev model,
with a prompt that describes how a pianist divides the notes (five fingers,
a reach of about a tenth, how fast a hand can leap, the left hand below the
right). Each request covers at most 1.5 s of music and shows the 3 s before
it (older notes no longer affect where a hand is) and 1.5 s after. It opens
by saying where each hand is placed when the section starts, and each note's
question says where both hands are, how far they are from the note, and
where they go next. It asks in three stages:

1. left to right, each window seeing the hands chosen before it;
2. every window again, with both sides known;
3. wherever the result is physically impossible (a chord too wide or with
   more than five notes for one hand, a leap too fast, crossed hands), with
   the problem spelled out, up to four rounds.

Chords that are still impossible are split at the most likely point that both
hands can reach, and remaining leaps are fixed by moving single notes to the
other hand where Jev finds that least unlikely. `SAMPLE_REQUEST=<file>` saves
one full request so you can read the prompt.

```
TYPESAFE_API_KEY=... node tools/video-render/hands.js <file.mid> tools/video-render/hands/<name>.json
```

`render.js` picks up `hands/<midi file name>.json` automatically (or the file
in `HANDS`). The split for `17_ethude1.mid` is included.

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
