# The green line on the Black Key's beret (1:14–1:18.4) to match 1:13

The five frames in `frames_to_fix/` already have the right colours everywhere except one thing: the thin green line
that runs across the pink beret. At 1:13 (`reference/REFERENCE_Z_12_at_1m13_53s.png`) that line is a dark green,
`#4a9661`. In the five frames it is a light mint (about `#80c08d`), so it looks paler. `BERET_LINE_reference_vs_now.png`
shows the berets side by side.

## Frames

1. `1_S_1.png`, arms crossed: 1:14.23 and 1:15.21
2. `2_S_15.png`, arms crossed, one eye raised: 1:14.64 and 1:15.79
3. `3_U_1.png`, looks up: 1:16.23
4. `4_S_3.png`, panic hops: 1:16.67–1:17.34
5. `5_S_4.png`, ducks: 1:17.55 until the piano lands

## The prompt (one frame at a time)

Attach the reference image and one frame, and paste:

```
The first image is the reference. The second image is the same character. Change ONLY the thin green line that
runs across his pink beret in the second image: make it the same dark green as the line on the beret in the
reference, #4a9661, with the same even, solid look. Keep the line exactly where it is, with the same shape and
the same thickness.
Do not change anything else: not the beret's pink, not the green strip on his side, not the cheeks, not the
black body, outline, face, arms, legs or shoes, and not the pose, size or position. Do not redraw the character.
Output: one PNG, exactly the same size as the second image, with a transparent background.
```

Save each answer with the same file name and send them back to Claude, who puts them in place of the current ones
(same size and place on screen) and rebuilds II → III.
