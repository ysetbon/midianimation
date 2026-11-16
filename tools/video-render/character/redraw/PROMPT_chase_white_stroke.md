# Prompt for ChatGPT: the I → II white key, sharp and with part I's black stroke

The white key in the I → II chase (`W_1`–`W_16`, 0:28.2–0:35.8) uses the original drawings. They have the right
hands and colours, but no black stroke around the figure. Part I has that stroke. This redraw gives them the same
stroke and makes them sharp.

Attach `redraw_chase_white_stroke.zip` to a new chat. It has:
- `grids/`: the 16 frames on 4 sheets (`9_chase_white_key_sheet01`–`04`), transparent, 2 × 2;
- `reference/reference_stroke.png`: an I → II frame now (no stroke) next to a part I frame with the stroke wanted;
- `sheets.csv`: which frame is in which cell.

Then paste:

```
I'm attaching a zip with 4 PNG sprite sheets of a cartoon character (grids/) and a reference image (reference/).
Each sheet is 1536 × 1024 with a transparent background and holds four frames in a 2 × 2 grid (one frame per
768 × 512 cell). The character is a cream rectangular card with a lilac edge on the left, a small black beret,
orange cheeks, small peach mitten hands and thin black arms and legs.

Redraw every sheet as a clean, sharp, high-resolution version of the same drawings, with one change: give the
character a thin, even black stroke all the way round the outside of the figure, like the frame on the right
in reference/reference_stroke.png. The stroke goes along the outer side of the lilac edge, around the top, right
side and bottom of the card, and around each hand. It is closed all the way round, with no gaps, and the same
thickness in every frame. Keep the light cream rim of the card inside the stroke.

The reference shows only the stroke. Keep everything else from these sheets, not from the reference:
- every frame's pose, size, position, direction, expression and proportions;
- the hands exactly as drawn in each frame: small peach mitten hands with little fingers and a thumb, in the
  same gesture. Don't turn them into plain circles. They only get the black stroke around them;
- the colours (cream face #fbdebb, lilac edge #9e9bfa, orange cheeks #fc9a47, light rim #fcf8e7);
- everything around the character, in the same place and without a stroke added: sweat drops, motion lines,
  dust clouds, the spin swirl and the speed blur in the last frame.

Keep the four frames in the same cells. Don't add anything: no shadow under the character, no glow or white halo
around it, no background, no lines between the cells. Output each sheet as a PNG, 1536 × 1024, with a
transparent background.

Work through all 4 sheets, and keep the stroke and the character the same from sheet to sheet.

When all 4 are done, give me one zip with grids/ (the 4 sheets, each with exactly the same file name as the one
you got) and sheets.csv (unchanged). Before you zip it, open every PNG again to check it isn't cut short or
broken, and redo any that is.
```

If ChatGPT stops partway, reply "continue with the next sheets".

When you send me the zip back, I'll check the stroke, hands and colours (and put the colours back exactly if they
drift), fit the frames onto the old drawings (`build/hd/make_hd.py`, folder `9_chase_white_key`), and show you a
before and after before rendering.
