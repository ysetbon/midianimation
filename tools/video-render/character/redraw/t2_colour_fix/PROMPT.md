# Recolour the Black Key's frames after the sleep (1:14–1:18.4) to match 1:13

The frame at 1:13 (`reference/REFERENCE_Z_12_at_1m13_53s.png`, standing with arms crossed after the sleep) has
the colours we want. The five frames after it (`frames_to_fix/`) were drawn from an older sheet and their colours are
a little off: the green strip is bluer, the cheeks are brighter green, and the beret and arms are paler. U_1 (he looks
up at the whistle, 1:16.23) is the furthest off: its greens are a light mint.

`COLOURS_reference_vs_now.png` shows the exact colours, measured from the drawings:

| Part | 1:13 (target) | now (S_1 / S_15 / S_3 / S_4) | now (U_1) |
|---|---|---|---|
| Green strip on his left side | `#70bd82` | `#60bc81` | `#70d498` |
| Cheeks | `#649b6d` | `#62a877`–`#6bb182` | `#70d396` |
| Beret | `#fcb6a6` | `#fcbcad` | `#fcbeb1` |
| Arms, legs | `#fcb6a7` | `#fbbaab` | `#fcbeb1` |
| Eyes, puff (white) | `#faf5f3` | `#fbf7f4` | `#fdfdfd` |

The black body, the black outline, the shoes and the gloves stay pure black.

## Frames (when each is on screen)

1. `1_S_1.png`, arms crossed, angry: 1:14.23 and 1:15.21
2. `2_S_15.png`, arms crossed, one eye raised: 1:14.64 and 1:15.79
3. `3_U_1.png`, looks up: 1:16.23
4. `4_S_3.png`, panic hops (also shown mirrored): 1:16.67–1:17.34
5. `5_S_4.png`, ducks with his hands on his head: 1:17.55, until the piano lands at 1:18.4

## The prompt (one frame at a time)

Attach the reference image and one frame to fix, and paste:

```
The first image is the reference: a black cartoon character with a pink beret, a green strip down his left side,
green cheeks and pink arms and legs. The second image is the same character in another pose. Recolour the second
image so every colour matches the reference exactly:
- the green strip: #70bd82, with the same light and shade as in the reference
- the cheeks: #649b6d
- the beret: #fcb6a6, its green band the same green as the strip
- the arms, hands' skin and legs: #fcb6a7
- the whites of the eyes and the puff: #faf5f3
Keep the black body, black outline, black gloves and black shoes pure black.
Change ONLY the colours. Keep the pose, the shape, the size, the outline, the face, the expression and every line
exactly as they are in the second image. Do not redraw, move, add or remove anything.
Output: one PNG, the same size as the second image, with a transparent background.
```

Save each answer with the same file name and send them back to Claude, who fits them in place of the old ones
(same size and position on screen, as with A_4) and rebuilds II → III.

## Or let Claude do it

Claude can also recolour these five frames directly from the measured colours, keeping every pixel's shading (as
`hd/recolor.py` does for the White Key). That is exact and needs no redraw; ask for it instead of the prompt.
