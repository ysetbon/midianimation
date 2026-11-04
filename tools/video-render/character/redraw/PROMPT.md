# Redraw prompts for ChatGPT

## Faster: whole sheets (4 frames at a time)

`grids/` has the frames packed into sheets (25 for the soft ones, folders 1–5; 35 more for the ok-but-not-great ones, folders 6–8), 2 × 2 like your hug sheets (1536 × 1024, white
background). Each sheet holds one character, and all frames in a folder are at the same size.
`grids/sheets.csv` says which frame is in which cell. Send ChatGPT one sheet at a time with this prompt,
plus the character line for its folder (below):

```
This image is a 2 × 2 sheet of four separate frames of the same cartoon character. Redraw the whole sheet
as a clean, high-resolution version of the same drawings.

Keep exactly four frames in the same 2 × 2 layout: each frame stays in its own cell, at the same size and
in the same position, standing on the same ground line. Keep every frame the same: the same pose, the same
direction it faces, the same expression, the same proportions, the same colours and the same style (bold
black outlines, flat colours with soft shading). Keep everything else in each frame in the same place:
motion lines, sparkles, music notes, flying piano keys, and the soft grey shadow on the ground if there is
one. If a cell is empty, leave it empty.

Do not add anything (no background, no floor, no text, no frame lines between the cells) and do not remove
anything. Do not merge the frames or let them overlap.

Output: one PNG, 1536 × 1024 (landscape), with a transparent background, crisp, smooth outlines.
```

Save the answer with the same file name as the sheet. If a frame comes out different (another pose or
face), redo just that sheet.

## Or: one frame at a time

Send one frame at a time: attach the PNG and paste the prompt below. Save each answer under the same
file name, in the same folder, and send them back to Claude to swap into the video. 97 frames in 5 folders;
`frames.csv` lists each one, its sprite key and where it is in the video.

These frames are small (about 200–300 px tall) and get enlarged about 2× in the video, which makes them soft.
A redraw about 1000 px tall or more makes them sharp.

### The prompt (for one frame)

```
Redraw this exact frame as a clean, high-resolution version of the same drawing.

Keep everything the same: the same character, the same pose, the same direction it faces, the same
expression, the same proportions, the same colours and the same style (bold black outlines, flat colours
with soft shading, cartoon look). Keep everything else that is in the frame, in the same place: motion
lines, music notes, flying piano keys, and the soft grey shadow on the ground if there is one.

Do not add anything (no background, no floor, no text, no new props) and do not remove anything.
Do not change the camera angle or crop.

Output: one PNG with a transparent background, 1024 × 1536 (portrait), the character centred and filling
most of the height, with crisp, smooth outlines.
```

If ChatGPT can't make the background transparent, a plain white background is fine.

## The character line per folder (add it after either prompt)

- `1_partI_white_key`, `7_partIII_white_key` and `8_coda_white_key` (the white key): `The character is a cream rectangular card with a lilac edge on the left, a small black beret, orange cheeks and thin black arms and legs.`
- `2_coda_brown_piano` and `3_crossing_brown_piano` (21 frames): `The character is a small brown upright piano with a wood-grain side, a sheet of music on top, pink cheeks, a white bandage on the front and four thin legs with yellow boots.`
- `4_coda_black_key`, `5_chase_black_key` and `6_partII_black_key` (the black key): `The character is a tall black key with a green stripe on its left side, a big pink cap with a green band, green cheeks, white eyes, pink arms and legs and black shoes.`

## Tips

- Do part I first: it's on screen for the whole first 28 seconds.
- In each folder, keep the same character design from frame to frame. If one comes out different
  (another face, other colours), ask ChatGPT to redo it next to an earlier good one.
- In the coda folders, only the frames listed are used, so you don't need any others.
