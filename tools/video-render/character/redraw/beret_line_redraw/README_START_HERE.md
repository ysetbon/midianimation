# Redraw the green line on the Black Key's beret (9 frames): first remove it, then draw it again

The thin green line that runs across the Black Key's pink beret should look like the ones in `reference/`: one
solid, smooth, even dark green stroke, `#4a9661`, no gaps, no blur. In the nine frames in `frames_to_fix/` it is too
thin, broken in places and blurry (`BERET_LINES_reference_vs_now.png` shows them against the reference). Patching it
does not work, so: remove the old line completely, then draw a new one along the same path.

## The references (what the line should look like)

- `reference/REFERENCE_1m13_Z_12.png`: the frame at 1:13, THE reference.
- `reference/GOOD_LINES_all_references.png`: 17 good berets on one sheet.
- `reference/good_lines/`: each of them alone, `*_actual_pixels.png` at its real size, `*_zoom3x.png` enlarged 3x
  so you can see the pixels:
  - `Z_12`, `Z_9`, `Z_10`, `Z_11`, `Z_1`, `Z_2`, `Z_4`: from the same sleep sheet, at the same scale as
    `1_Z_5`–`4_Z_8`. Copy their line exactly for those four frames: same thickness, same colour, same edges.
  - `A_1`, `A_10`, `A_16`, `B_3`, `B_10`, `C_1`, `C_9`, `C_13`, `D_1`, `D_5`: part II, the same character in the
    same style as `5_S_1`, `6_S_15`, `7_U_1`, `8_S_3`, `9_S_4`.

## The frames

| File | On screen at | Line thickness in this file |
|---|---|---|
| `1_Z_5.png` – `4_Z_8.png` | 1:10.9–1:12.5, asleep on the floor | 4 px |
| `5_S_1.png`, `6_S_15.png` | 1:14.2–1:15.8, arms crossed | 5 px |
| `7_U_1.png` | 1:16.2, looks up (a big file) | 11 px |
| `8_S_3.png`, `9_S_4.png` | 1:16.7–1:18.4, panic and duck | 5 px |

(`frames.csv` has the same list. The files are at different scales; these thicknesses make every line, on screen, as
thick as at 1:13.)

## The guides (where the line goes)

`guides/old_line_paths.json` has, for each frame, the centre of the old line traced point by point, in that file's
own pixels (x, y), from one end to the other. `guides/<frame>_old_line_path_in_red.png` shows that path in red on the
frame. Use it so the new line follows exactly the old line's path, starts and ends in the same places, and keeps its
curve.

## Step 1: remove the old line

In each frame, paint out the old green line completely: every green pixel of the line and its soft greenish edge
becomes the beret's own pink, taken from the beret right next to it (keep the beret's light and shade, so no patch
shows). When step 1 is done the beret must be clean pink with no trace of green, except where the beret meets the
green strip on his side, which stays. Save this to `fixed/step1_line_removed/<same file name>` so it can be checked.

## Step 2: draw the new line

On the clean beret from step 1, draw one new stroke along the guide path:
- colour `#4a9661`, flat (no lighter centre, no blotches);
- the thickness from the table, even along the whole length; the ends may taper slightly, as in the references;
- one continuous stroke with crisp anti-aliased edges: no gaps, no blur, no jagged steps;
- where it meets the beret's black outline or the green strip, it joins cleanly, as in the references.

Save the result with the same file name in `fixed/`.

## Do not change anything else

Every pixel outside the beret line and its immediate edge stays exactly as it is. Each image keeps its exact size
and its exact alpha channel (the line is inside the beret, so no transparency changes).

## Check before you finish

For every output: the same size and alpha as the input; nothing changed further than about 3x the line's thickness
from the path; the line's colour within about 6 levels of `#4a9661`; its thickness within 1 px of the table along its
length; no gaps; and, in the step 1 file, no green left on the beret. Write `fixed/report.csv` (file, thickness,
colour, gaps found, pixels changed) and zip the whole `fixed/` folder, including `step1_line_removed/`.

Send the zip back to Claude, who checks each line against the references, puts the frames in place and rebuilds the
video.
