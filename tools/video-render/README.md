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
| `10_hands_blocks` | Right hand as two layered brushes (a soft glow under triangles), left hand as blocks; each note disappears the moment its MIDI length ends, and notes are played at 40% of the screen width. Only when a hand split exists |
| `11_sections` | A look per section of the piece, split by hand: each section has its own shape and palette and flashes as its notes are struck; each transition animates differently (see *Sections* below). Only when a hand split and a sections file exist |
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

Where the line is not exact enough, notes can be pinned to their attacks by
hand (the sync desk artifact saves them) and passed in `AUDIO_PINS` as a JSON
list of `{ "tick": <MIDI tick>, "recordingTime": <seconds> }`. The sync then
runs through every pin, and keeps the measured speed before the first and
after the last.

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

`midi/17_ethude1.mid` is the étude with one note removed: the A3 at tick
18121 (98.52 s in the recording), which made the left hand's chord E2–E3–A3
too wide to strike; the A is still played by the right hand (A4). Every other
event is unchanged, so the recording sync still applies.

`remove_note.py` takes the same A3 out of the recording itself: it cuts only
the A3 partials no other note of the chord shares (220, 1102, 1545, 2455,
2919 and 3388 Hz), only while the note sounds (98.2–98.95 s), so everything
else in the recording is unchanged.

## Sections

`sections/<midi file name>.json` (or the file in `SECTIONS`) divides the
piece into sections and the transitions between them, each starting at a MIDI
tick. For `17_ethude1.mid`: I on E (circles), the move to D, II in D major
(triangles), the move to A, III in A major (blocks), the move to the coda, and
the coda (stars). Each section has three palettes (`SECTION_LOOKS` in
`jobs.js`); `palettes` in the file, or `SECTION_PALETTES=A,B,C,A`, picks one
per section, and `shapes`, or `SECTION_SHAPES=2,3,1,7`, its shape (the
numbers in `brushShapes`, `reducers/brushes.js`). Palette C follows
Scriabin's key colours.

Notes in a section flash when struck. Across a transition the notes turn
gradually, note by note, from the previous section's shape, size and colours
into the next section's (the brush's morph, see below), and each note turns
wholly into the next section's colours the moment it is struck, so colours
change from one note to the next, never partway along a note. Every note keeps its MIDI length.

`SECTION_JUMP=<height>:<length>:<velocity>[:both|R|L]` (or `jump` in the
sections file) makes every struck note leap and land: height in pitch steps,
length in seconds, and how much louder notes leap higher (0 to 1), for both
hands or one. For example `SECTION_JUMP=5:0.4:0.5:both`. The brush panel has
the same three settings (jump when struck, jump length, jump follows velocity).

`plan` in the sections file gives each part and crossing a movement for its
struck notes (`move`, `strength`, `len` in seconds, `vel`: how much louder
notes move more, and for a crossing `peak`). For `17_ethude1.mid`: jump in I
(the same jump as `SECTION_JUMP=5:0.4:0.5`), burst across I → II, rise in II,
shake across II → III, squash in III, ripple across III → Coda and echo in the
coda. A crossing blends in: the part's movement fades as the crossing's grows,
the crossing's reaches full strength at `peak` (50%, halfway) and stays there
to the end of the crossing, and the next part starts with its own movement at
full strength. Each note takes the blend of the moment it is struck.

In the renderer these are a brush's `motions` (`type`, `strength`, `length`,
`velocity`, and optional `fadeIn` / `fadeOut` as `[from, to]` in seconds).
Jump, rise and shake move the note, squash changes its proportions, and
ripple, echo and burst are drawn around it by a second, small shader.

`SECTION_PLAY=5|6|7` changes how the parts' notes are coloured as they play:
5 fades to white over the note, 6 flashes, keeps the note's colour, turns it
white over the last 40% and fades it out over the last 15%, and 7 turns the
note white with its movement before burning out like 6 (4, the default,
flashes and fades back). 8 (for crossings) flips to the next part's colour
when struck and then burns out like 6. `endings` in the sections file gives
each zone its own play mode; for `17_ethude1.mid` part I burns out, the
crossings into II and into the coda flip and burn out, II lights with its
rise, the crossing into III flips with a hard cut, III burns out and the coda
flips to its bright colour and burns out. `SIZE=1280x720` renders smaller, for previews.

`DUMP_SCENE=<file>` saves what the renderer draws for the first job named
(brushes, notes with their velocities, the synced tempo map) instead of
rendering. A page that loads the repo's renderer can then draw exactly the
same frames live, as the motion lab artifact does.

The app's brushes can do this too: a brush with `morphShape` turns the notes
struck between `morphStart` and `morphEnd` (seconds) gradually into that
shape, and into `morphSize`, `morphSizeCurve`, `morphLeftColor` and
`morphRightColor` when given. Shapes are blended through their outlines, so
in between they take intermediate forms rather than cross-fading. Diamond,
ring and star are new shapes alongside rectangle, circle, triangle and blob.

```
AUDIO=recording.wav AUDIO_SYNC=1.0434:0.04 SECTION_PALETTES=A,A,A,A node tools/video-render/render.js 17_ethude1.mid out 11_sections
```

To have Jev review a finished split without changing it:

```
node tools/video-render/hands.js --review <file.mid> hands/<name>.json proposals.json
```

Jev sees every note with the hands around it and proposes switching a note
only when it is at least 80% sure. A proposal is kept as a suggestion only if
it makes none of the checks worse, and notes that the rules set against Jev's
first answer (the corrections behind the register, idle-hand and figure
rules) are never proposed for switching back.

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
