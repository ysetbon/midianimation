# Sleep frames: beret line to match the frames around them

The Black Key sleeps at 1:10.9–1:12.6 (Z_5–Z_8). The green line on his beret in these four frames was redrawn in the last
pass, but it came out about half as thick and lighter than in the sleep frames right before (Z_4) and right after (Z_9),
so it flickers thin/thick as he falls asleep and wakes. The user marked these four to fix and picked Z_1–Z_4 and
Z_9–Z_12 as the references.

## What is in here

- `frames_to_fix/` — the 4 frames as they are in the video now (1_Z_5, 2_Z_6, 3_Z_7, 4_Z_8). Fix these.
- `reference/Z_*_full.png` — the 8 good frames, same scale as the frames to fix. **Z_4 (just before) and Z_9 (just after) are the
  best models**: same lying/sleeping view, the line should look like theirs.
- `reference/good_lines/` — each reference's beret, at actual pixels and 3x zoom.
- `reference/ALL_8_REFERENCES.png` — the 8 berets on one sheet.
- `COMPARE_references_vs_now.png` — Z_9 and Z_4 (top, yellow) against the four frames now.
- `guides/` — the current line's path drawn in red on each frame, and `line_paths.json` (x, y points per file).
- `frames.csv` — when each frame is on screen and what to match.

## What to do, per frame

1. **Remove** the current green line: paint it out with the beret's pink, so there is no seam, ghost or darker trace left.
2. **Redraw** it along the same path (the red guide), so it sits where it is now:
   - thickness **about 6–7 px in the file** (now about 3.5), like Z_4 and Z_9;
   - colour: solid dark green like the references, core **about #208349 (Z_4) to #3f885a (Z_9)** — not the light #4a9661;
   - smooth anti-aliased edges, the ends tapering into the black outline as in the references.
3. **Keep everything else exactly**: the file size in pixels, the alpha (transparency), the pink of the beret, the black outline,
   body, face, green strip, the white Z letters. Do not re-render the beret or the drawing; only the line changes.

## What to send back

`returned/` with the 4 files under the same names (1_Z_5.png ... 4_Z_8.png), and `returned/step1_line_removed/` with the
4 frames after step 1 — all zipped as `sleep_lines_fixed.zip`.
