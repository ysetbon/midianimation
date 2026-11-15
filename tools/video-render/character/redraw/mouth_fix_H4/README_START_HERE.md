# Remove the line under the tongue (White Key, H_4 and H_5)

In the drawings around 1:46 the White Key's open mouth is black on top with a pink tongue at the bottom, and **the pink
tongue meets the cream face directly**: there is no dark line under it (H_1, H_6, H_8, H_9, H_10 in `reference/`).
In **H_4** (on screen 1:45.89–1:46.17) a thin dark line runs along the bottom of the tongue, so his mouth flickers
between "outlined" and "not outlined" as the frames change. **H_5** (1:46.90–1:47.04) has the same line; fixing it is
optional (it is on screen for only 0.14 s), but please do both.

## Files

- `frames_to_fix/1_H_4.png`, `frames_to_fix/2_H_5.png` — work on these, at this size (twice the stored size, so the edit is easy to place; they are shrunk back afterwards).
- `problem_maps/*_problem.png` — the mouth up close with the line marked (yellow, 1); `*_where.png` — the whole drawing with the mouth circled.
- `COMPARE_now_vs_references.png` — H_4 and H_5 against the five good mouths.
- `reference/mouths_zoom4x/` — the good mouths up close; `reference/full_drawings/` — the whole drawings.

## What to do

1. Remove only the thin dark line along the **bottom edge of the pink tongue**. Where it was, the tongue's pink now meets the cream face directly, with the same soft anti-aliased edge the references have.
2. Keep the tongue's shape and its pink exactly as they are; keep the black of the mouth above the tongue and its outline at the top and sides exactly as they are.
3. Change nothing else: eyes, cheeks, card, outline, arms, everything else pixel for pixel the same. Same file name, same pixel size, transparent background stays transparent.

## Send back

`returned/1_H_4.png` and `returned/2_H_5.png`, zipped as `mouth_fixed.zip`.
