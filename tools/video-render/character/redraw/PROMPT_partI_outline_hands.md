# Prompt for ChatGPT: part I white key, the same black stroke everywhere and the real hands

The part I redraws aren't the same from frame to frame:
- the black stroke around the figure: sheets 01–09 have a thin black stroke all the way round the outside of the
  figure (the lilac edge, the card, the hands). Sheets 10 and 12 have none, and sheet 11 has it only in places.
  Every frame should have the full stroke, like sheets 01–09;
- the hands: in many frames they are plain round circles. The originals have small peach mitten hands with
  little fingers and a thumb.

Then the same fix goes to the other parts with the white key (I → II, part III, coda), using part I as the model.

Attach `redraw_partI_outline_hands.zip` to a new chat. It has:
- `grids/`: the 12 part I sheets the video uses now (shadow-free and in the right colours);
- `originals/`: the same 12 sheets from the original small drawings, with the same layout. Each one is named like
  its grid sheet with `_original` added. They show the right hands;
- `reference/reference_stroke_wrong_vs_right.png`: no stroke (sheet 10), a stroke only in places (sheet 11), and
  the full stroke (sheet 01), on the video's background;
- `reference/reference_hands_close_up.png`: close-ups of the original hands (their shape);
- `sheets.csv`.

Then paste:

```
I'm attaching a zip with 12 PNG sprite sheets of a cartoon character (grids/), the original drawings they were
redrawn from (originals/), and two reference images (reference/). Each sheet is 1536 × 1024 with a transparent
background and holds four frames in a 2 × 2 grid (one frame per 768 × 512 cell). originals/ has the same 12
sheets, in the same layout: grids/X.png goes with originals/X_original.png, with the same frame in the same cell.
The character is a cream rectangular card with a lilac edge on the left, a small black beret, orange cheeks and
thin black arms and legs.

Fix two things in every frame of grids/:

1. The black stroke around the figure. Sheets 01 to 09 have a thin, even black stroke traced all the way round
   the outside of the character: along the outer side of the lilac edge, around the top, right side and bottom
   of the card, and around each hand. That is the look I want. Sheets 10 and 12 have no stroke, and sheet 11 has
   it only in places. Give every frame of every sheet the same full black stroke as sheets 01 to 09: closed all
   the way round, with no gaps, the same thickness as in sheets 01 to 09. See
   reference/reference_stroke_wrong_vs_right.png. Keep the light cream rim of the card inside the stroke, as in
   sheets 01 to 09. If a frame of sheets 01 to 09 has a gap in its stroke, close it too.

2. The hands. In many frames the hands are just plain round circles. Redraw each hand like the same hand in the
   same frame of the original sheet (see also reference/reference_hands_close_up.png for the shape): a small
   peach mitten hand with little fingers and a thumb, pointing the same way and in the same gesture (open, fist,
   waving, pointing) as in the original, at the end of the black arm, the same size as now, and with the same
   thin black stroke around it as the rest of the figure (like the hands on the right in
   reference/reference_stroke_wrong_vs_right.png).

Change nothing else. Keep every frame exactly as it is: the same pose, size, position, colours (cream face
#fbdebb, lilac edge #9e9bfa, orange cheeks #fc9a47, light rim #fcf8e7), beret, face, legs, feet, sparkles and
white motion lines, and the four frames in the same cells. Don't add anything: no shadow under the character,
no glow or white halo around it, no background. Output each sheet as a PNG, 1536 × 1024, with a transparent
background.

Work through all 12 sheets. For every frame, look at its original before you finish its hands, and keep the
stroke and the hands the same from sheet to sheet: compare each sheet with sheet 01.

When all 12 are done, give me one zip with grids/ (the 12 sheets, each with exactly the same file name as the
one you got, without "_original") and sheets.csv (unchanged). Before you zip it, open every PNG again to check
it isn't cut short or broken, and redo any that is.
```

If ChatGPT stops partway, reply "continue with the next sheets" until all 12 are done.

When you send me the zip back, I'll check the stroke, hands and colours (and put the colours back exactly if they
drift), fit the frames, and show you a before and after before rendering.

## Next: the other parts with the white key

Once part I is done, it becomes the model for the same stroke and hands on:
- I → II chase (`W_*`): the original drawings, which have no black stroke, so it needs adding;
- part III (`E`–`H`) and the coda white key (`J`), from the round 2 redraws: check each frame's stroke and hands.
