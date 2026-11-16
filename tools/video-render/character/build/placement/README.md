# Checking where the characters stand

Two helpers used for the placement plan of 2026-11-11 (the plans themselves are made by `../stage.py` inside each part's script).
Both read the same settings as a build: `B` (this `build` folder), `SRC` (the notes render), `TIMEMAP`, `TIMEMAP_END`,
`TIMEMAP_SHIFT`, `HUGSEQ` and `NOTE_LEFT` (the `notes_left.json` a build writes).

- `measure.py <part> <out.json>`: for every video frame of `partI`, `chase`, `partII`, `t2`, `partIII` or `coda`, each
  character's pose and outline (left, right, top, bottom in px).
- `still.py <part> <outdir> <video seconds ...>`: full frames of a part at those video times.
