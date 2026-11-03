# Prompt for ChatGPT: part III white key, part I's black stroke and the real hands

Part III's white key (`E_1`–`H_16`, 1:21.0–1:51.9) uses the round 2 redraws. Almost none of them have the black
stroke around the figure that part I and I → II have now, and the hands are small and simplified. This redraw
gives them the same stroke and hands as part I.

Attach `redraw_partIII_stroke_hands.zip` to a new chat. It has:
- `grids/`: the 16 part III sheets the video uses now (62 frames; two cells are empty), transparent, 2 × 2;
- `originals/`: the same 16 sheets from the original small drawings, with the same layout. Each one is named like
  its grid sheet with `_original` added. They show each frame's hands;
- `reference/reference_stroke.png`: a part III frame now (no stroke) next to a part I frame with the stroke and
  hands wanted;
- `sheets.csv`: which frame is in which cell.

Then paste:

```
I'm attaching a zip with 16 PNG sprite sheets of a cartoon character (grids/), the original drawings they were
redrawn from (originals/), and a reference image (reference/). Each sheet is 1536 × 1024 with a transparent
background and holds four frames in a 2 × 2 grid (one frame per 768 × 512 cell; an empty cell stays empty). originals/ has the same 16
sheets, in the same layout: grids/X.png goes with originals/X_original.png, with the same frame in the same cell.
The character is a cream rectangular card with a lilac edge on the left, a small black beret, orange cheeks,
small peach mitten hands and thin black arms and legs.

Fix two things in every frame of grids/:

1. The black stroke around the figure. Give the character a thin, even black stroke all the way round the outside
   of the figure, like the frame on the right in reference/reference_stroke.png: along the outer side of the
   lilac edge, around the top, right side and bottom of the card, and around each hand. It is closed all the way
   round, with no gaps, and the same thickness in every frame. Keep the light cream rim of the card inside the
   stroke. In the frames where the card is seen from the side (a thin strip), the stroke goes round that strip.

2. The hands. Redraw each hand like the same hand in the same frame of the original sheet: a peach mitten hand
   with little fingers and a thumb, in the same gesture (open, fist, waving, clapping) and pointing the same way,
   at the end of the black arm. Make them the size of the hands in the reference's right frame, not tiny, and
   give them the same black stroke as the rest of the figure.

The reference shows only the stroke and the hands. Keep everything else from these sheets, not from the reference:
- every frame's pose, size, position, direction, expression and proportions, and the four frames in the same
  cells;
- the colours (cream face #fbdebb, lilac edge #9e9bfa, orange cheeks #fc9a47, light rim #fcf8e7);
- everything around the character, in the same place and without a stroke added: the yellow sparkles, the yellow
  motion lines and the yellow spin rings.

Don't add anything: no shadow under the character, no glow or white halo around it, no background, no lines
between the cells. Output each sheet as a PNG, 1536 × 1024, with a transparent background.

Work through all 16 sheets, in the order of their file names. Keep the stroke, the hands and the character the
same from sheet to sheet: compare each sheet with the first one you did.

When all 16 are done, give me one zip with grids/ (the 16 sheets, each with exactly the same file name as the one
you got, without "_original") and sheets.csv (unchanged). Before you zip it, open every PNG again to check it isn't
cut short or broken, and redo any that is.
```

If ChatGPT stops partway, reply "continue with the next sheets" until all 16 are done.

When you send me the zip back, I'll check the stroke and hands, put the colours exactly on the I → II target (part
III's redraws drifted a little more yellow, cream about #ffe4b7, and a stronger lilac), fit the frames, and show
you a before and after before rendering.

## Next

The coda white key (`J`, 3 sheets in `8_coda_white_key`), same prompt.
