# Recolour the Black Key to his colours at 1:13 (102 frames, one pass)

The Black Key (black card with a pink beret and a green strip) should have the same colours all through the video.
His frame at 1:13 is right: `reference/REFERENCE_1m13_Z_12.png`. In the other parts his greens are too bright or
mint, his beret line is too light, and in the ending's hug drawings his body is dark teal instead of black.
`reference/how_it_looks_now_across_the_video.png` shows him now at ten moments; `frames.csv` lists every frame, when
it is on screen, and its colours now.

## The target colours (measured on the 1:13 frame)

| Part | Colour |
|---|---|
| Body, outline, gloves, shoes, eyebrows | pure black `#000000` |
| Green strip down his left side | `#70bd82` |
| Cheeks | `#649b6d` |
| Beret | `#fcb6a6` |
| The thin line across the beret | `#4a9661` (dark green, clearly darker than the strip) |
| Arms and legs (skin) | `#fcb6a7` |
| Whites of the eyes, the white puff | `#faf5f3` |

Keep the shading: a part that is lighter or darker in places (a highlight on the strip, a shadow on the beret) stays
lighter or darker by the same amount around its new colour. Keep the soft edges where colours meet.

## The folders

| Folder | Frames | When | What to change |
|---|---|---|---|
| `1_after_the_sleep/` | 5 | 1:14–1:18 | ONLY the line across the beret (to `#4a9661`). Everything else is already right. |
| `2_crossing/` | 16 | 0:29–0:38 | All his colours, to the table above. |
| `3_part_II/` | 61 | 0:36–1:09 | All his colours, to the table above. |
| `4_coda_fall/` | 13 | 1:53–1:59 | All his colours (the strip is a bright mint here, the furthest off). |
| `5_coda_hugs/` | 7 | 1:59–2:10 | ONLY the Black Key's colours, including his body to pure black (it is dark teal now). These drawings also show the White Key (cream card, lilac strip, black beret, orange cheeks) and sometimes the Brown Piano: do NOT change them. |

## Rules for every frame

1. Change colours only. Do not redraw, move, resize, crop, sharpen or blur anything. Every line, shape and
   expression stays exactly as it is.
2. Same pixel size as the input, transparent background, the same transparency (alpha) on every pixel.
3. Save the result as PNG with the same file name in `fixed/<same folder>/` (for example
   `fixed/3_part_II/A_1.png`). Leave the original files untouched.
4. Some frames do not show every part (the strip can be hidden, the beret line can be under a hand): recolour what is
   there and add nothing.

## Check before you finish

For each output, measure the median colour of the strip, the beret, the beret line and the body (or cheeks) and
compare with the table: each should be within about 6 levels per channel. Compare each output with its input: the
alpha channel must be identical, and pixels that are not part of the Black Key (the White Key and the piano in
`5_coda_hugs/`) must be unchanged. Write `fixed/report.csv` with, for each file, the measured colours after and
any frame you could not fix.

When done, zip the `fixed/` folder and send it back to Claude, who puts every frame in place (same size and position
in the video) and rebuilds the video.
