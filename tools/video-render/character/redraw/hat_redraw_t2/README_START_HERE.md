# Redraw the beret in 5 frames (1:14–1:19)

After he wakes up (1:14–1:19, until the piano lands on him) the Black Key's beret is soft and smudged: the outline is
blurry, the brim's tip and underside smear pink into the green strip, and in places the outline is missing. Part II's
berets (in `reference/`) are crisp. Make these five like them.

## Files

- `frames_to_fix/` — the 5 frames to fix. **Work on these files at this size.** Files 1, 2, 4, 5 are twice the size they show on screen (so the new beret comes out sharp when shrunk); 3_U_1 is its normal size.
- `problem_maps/` — each frame with **numbered yellow circles** on what is wrong, and the note for each under the picture (also in `problems.csv`, with x, y in the file's pixels).
- `HAT_SPEC.md` — colours and widths in pixels for each file, and which references fit each frame.
- `reference/ALL_REFERENCE_HATS.png` — the 12 good hats on one sheet; `reference/hats_closeup/` each one at the same size as the hats you draw; `reference/full_drawings/` the whole drawings.
- `guides/*_line_path_blue.png` — where the green line runs now (blue). Keep the line on this path. `guides/frames.json` has the path as points.

## Do it in three steps per frame, and save each step

1. **Clean** (`returned/step1_clean/`): inside the beret only, remove the green line and repaint the beret as flat pink `#fcb6a6`. Keep the beret's outer shape and position. Remove every smudge: where pink and green mix at the brim, decide which is beret (pink) and which is strip (green).
2. **Outline** (`returned/step2_outline/`): draw a crisp black outline all the way round the beret, at the width in `HAT_SPEC.md`, **including the brim's tip and its underside**, where it sits over the green strip and the body. Fix every numbered spot in the problem map. The brim must look like the brims in C_5, C_13, D_1, Z_12.
3. **Line** (`returned/`, the final file): draw the green line along the blue path, solid green `#46955e`, at the width in `HAT_SPEC.md`, both ends ending cleanly at the outline like the references.

## Keep everything else exactly as it is

- Same file name, **same pixel size**, PNG with transparency.
- Only the beret changes. Body, face, eyes, cheeks, green strip, arms, gloves, the raised fist (S_3), the hand on the beret (S_4), sweat drops: pixel for pixel the same. Where the fist or hand is in front of the beret, it stays in front.
- The transparent background stays transparent. The beret's outer shape and position stay the same (you may smooth a ragged edge by a few pixels).
- No new shading, texture, gradient or glow on the beret. Flat colour like the references.

## Send back

`returned/` with the 5 final files (same names), `returned/step1_clean/` and `returned/step2_outline/` with 5 files each, zipped as `hats_redrawn.zip`.
