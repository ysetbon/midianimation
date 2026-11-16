# MIDI Animation

Animated music videos made from a MIDI file and a recording: the notes play as moving shapes on the right, and
cut-out cartoon characters act out the music on the left, every pose landing on a note.

The first one is **Capriccio for Piano – Yonatan Setbon** (étude 1): a White Key, a Black Key and a Brown Piano
across three parts and a coda, 2:10.9 at 1080p. The latest final is
`tools/video-render/character/output/etude1_final_43.mp4`.

## Where to start

| | |
|---|---|
| **The website** | `docs/index.html`: what was made, how, the whole pipeline as a diagram, and a planner to start a new video. Open it in a browser, or publish it with GitHub Pages (Settings → Pages → branch `master`, folder `/docs`). |
| **The playbook** | [`tools/video-render/PLAYBOOK.md`](tools/video-render/PLAYBOOK.md): every workflow, the lessons learned, and what to change for other music, characters, movements or backgrounds. |
| **The notes renderer** | [`tools/video-render/README.md`](tools/video-render/README.md): renders the notes of a MIDI file to video in headless Chromium, with hand split, sections, note movements and sync to a recording. |
| **The characters and the build** | [`tools/video-render/character/build/README.md`](tools/video-render/character/build/README.md): every part's character, colours and transitions, and the final video. |
| **The log** | [`CLAUDE.md`](CLAUDE.md): every final (21 to 43) and every choice behind it. |

## Quick start

```sh
cd tools/video-render && npm install
# the notes (see the playbook for the étude's settings)
node render.js midi/17_ethude1_27.mid out 11_sections
# the final, with the latest settings, from the notes render kept in the repo
character/build/build_latest.sh out/final etude1_final_NN.mp4
```

Needs Node 18+, Python 3 with numpy, scipy and Pillow, and ffmpeg.

## Credits

The notes are drawn by the WebGL renderer of [MuVis](https://github.com/sytzez/muvis) by sytzez: the files at the
repo root (`midiLoader.js`, `reducers/`, `renderer/`, `color.js`, `environment.js`, `resolutions.js`,
`midi-parser-js.js`) are from MuVis, extended with section looks, note movements and shape morphs. MuVis's browser
editor was removed from this repo on 2026-11-16 (it is in the git history and in the original project). The music,
the drawings' direction and every choice are Yonatan Setbon's; the code was written with Claude Code, and the
drawings were made with ChatGPT and Codex.
