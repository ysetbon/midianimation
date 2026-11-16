# Prompt for ChatGPT, round 2 (paste into a new chat, with the zip attached)

```
I'm attaching a zip with 35 PNG sprite sheets for a short cartoon music video. Each sheet is 1536 × 1024 on a
white background and holds four frames of one character in a 2 × 2 grid (one frame per 768 × 512 cell, an
empty cell stays empty). The drawings are small and look soft when the video enlarges them. Please redraw every
sheet as a clean, high-resolution version of the same drawings.

The characters:
- Files starting with 6_partII_black_key: a tall black key with a green stripe on its left side, a big pink cap
  with a green band, green cheeks, white eyes, pink arms and legs and black shoes.
- Files starting with 7_partIII_white_key and 8_coda_white_key: a cream rectangular card with a lilac edge on
  the left, a small black beret, orange cheeks and thin black arms and legs.

For every sheet:
- Keep exactly four frames in the same 2 × 2 layout. Each frame stays in its own cell, at the same size and in
  the same position, standing on the same ground line. Don't merge frames or let them overlap.
- Keep every frame the same: the same pose, the same direction it faces, the same expression, the same
  proportions, the same colours and the same style (bold black outlines, flat colours with soft shading).
- Keep everything else in each frame in the same place: motion lines, sweat drops, sparkles, steam puffs,
  little marks, and the soft grey shadow on the ground if there is one.
- Don't add anything (no background, no floor, no text, no lines between the cells) and don't remove anything.
- Output: a PNG, 1536 × 1024, transparent background, crisp smooth outlines.

Work through all 35 sheets, in the order of their file names. Keep the same character design from sheet to
sheet: compare each new sheet with the ones you've already done, and redo any frame that comes out with another
face, other colours or a different pose.

When all 35 are done, give me one zip with:
- grids/ - the 35 redrawn sheets, each with exactly the same file name as the sheet you got;
- sheets.csv - the same file I sent, unchanged.

Before you zip it, open every PNG again to check that it isn't cut short or broken, and redo any that is.
```

## Notes

- The zip to attach is `redraw_round2_sheets.zip`: the 35 sheets in `grids/` and `sheets.csv`.
- If ChatGPT stops partway (it may only do a few sheets per answer), reply "continue with the next sheets"
  until all 35 are done, then ask for the zip.
- Send the zip back to me and I'll fit each frame onto the old drawing and re-render, as with round 1.
