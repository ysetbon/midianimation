# Hat spec (measured on the 12 reference hats, scaled to each frame)

Every hat has three parts, all crisp, flat cartoon colour with clean anti-aliased edges (no blur, no smudge, no texture):

| Part | Colour | Width |
|---|---|---|
| Beret fill | flat pink `#fcb6a6` (same as now) | – |
| Outline, all the way round the beret, including the brim's tip and underside | black `#000000` | about 2.7% of the beret's width |
| Green line (the band) | solid green, core `#46955e` | about 2.2% of the beret's width |

The green strip on his body (`#70bd82`), his body (black), face, eyes, cheeks, arms, gloves, fist, sweat drops: **unchanged**.

## Per frame, on the canvas in `frames_to_fix/`

| File | Beret width | Outline | Green line | Best references |
|---|---|---|---|---|
| 1_S_1.png | 520 px | 14 px | 11 px | Z_12 (same pose, the frame before), C_5, C_13 |
| 2_S_15.png | 520 px | 14 px | 11 px | Z_12, C_5, C_2 |
| 3_U_1.png | 636 px | 17 px | 14 px | Z_9 (tilted), C_1, D_1 |
| 4_S_3.png | 524 px | 14 px | 11 px | C_13 (fist at the beret), C_5, Z_12 |
| 5_S_4.png | 518 px | 14 px | 11 px | C_13, C_15, B_5 |

The close-ups in `reference/hats_closeup/` are all 520 px wide, the same size as the hats in files 1, 2, 4 and 5, so widths can be compared directly.

## The brim (the part that is wrong in every frame)

Look at C_5, C_13, D_1, Z_12: the brim's tip sticks out to the left as a clean pointed shape. Its **underside has its own black outline**, and below that outline the green strip and the black body start cleanly. No pink fading into green, no green fading into pink.
