# Redraw the green line on the Black Key's beret (9 frames)

The thin green line that runs across the Black Key's pink beret is right at 1:13
(`reference/REFERENCE_1m13_Z_12.png`): one solid, smooth, even dark green line, `#4a9661`, about 4.7 px thick on
screen. In these nine frames it is too thin, broken in places and blurry (see `BERET_LINES_reference_vs_now.png`).
Its colour is already close; what is wrong is its shape.

| File | On screen at |
|---|---|
| `1_Z_5.png` – `4_Z_8.png` | 1:10.9–1:12.5, asleep on the floor |
| `5_S_1.png`, `6_S_15.png` | 1:14.2–1:15.8, arms crossed |
| `7_U_1.png` | 1:16.2, looks up |
| `8_S_3.png`, `9_S_4.png` | 1:16.7–1:18.4, panic and duck |

`frames.csv` gives, for each file, how thick to draw the line in that file's own pixels (the files are at different
scales: 4 px in the sleep frames, 5 px in S_1, S_15, S_3, S_4, 11 px in U_1), so that on screen it is as thick as at
1:13.

## What to do in each frame

1. Find the line as it is now: it runs across the beret, near its lower edge, from one side of the beret to the
   other (in some frames a hand or the edge of the beret hides part of it).
2. Redraw it along the same path (the same start, end and curve), as one continuous, smooth, solid stroke:
   - colour `#4a9661`, flat, no lighter centre, no blotches;
   - the thickness from `frames.csv`, even along its whole length (the ends may taper slightly, as in the reference);
   - crisp anti-aliased edges, no blur, no gaps.
3. Where the old line was wider, thinner or ragged, the pixels around the new stroke become the beret's pink again
   (the same pink as the beret next to them).
4. Change nothing else: every pixel outside the beret line and its immediate edge stays exactly as it is; the image
   keeps its exact size and its exact alpha channel (the line is inside the beret, so no transparency changes).

A coding agent can do this exactly: trace the old line's centre line (the middle of its green pixels), smooth it,
paint a new anti-aliased stroke of the given width in `#4a9661` along it, and paint the beret's local pink over the
old line's pixels that the new stroke does not cover.

## Output and check

Save each result with the same file name in `fixed/`. Then check every output: the same size and alpha as the
input; outside a band of about 3x the line's thickness around the line, every pixel unchanged; the line's colour
within about 6 levels of `#4a9661`; its thickness within 1 px of `frames.csv` along its length; no gaps. Write
`fixed/report.csv` (file, measured thickness, measured colour, pixels changed) and zip the `fixed/` folder.

Send the zip back to Claude, who puts the frames in place and rebuilds the video.
