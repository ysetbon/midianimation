# Prompt for ChatGPT: part I white key, no black outline and the real hands

The part I redraws drew two things that aren't in the original drawings:
- a thin black line traced around the outside of the whole figure: along the outer side of the lilac edge, around
  the top, right side and bottom of the card, and as a black ring around each hand. In some frames it goes all
  the way round, in others only part of the way. The originals and the I → II chase have no such line: the lilac,
  the cream rim and the peach hands meet the background directly;
- the hands as plain round blobs. The originals have small peach mitten hands with little fingers and a thumb.

Attach `redraw_partI_outline_hands.zip` to a new chat. It has:
- `grids/`: the 12 part I sheets the video uses now (shadow-free and in the right colours);
- `originals/`: the same 12 sheets from the original small drawings, with the same layout. Each one is named like
  its grid sheet with `_original` added. They show the right hands and the edge with no outline;
- `reference/reference_chase_first_frame.png`: the white key in the first frame of the I → II chase (the edge and
  colours to match);
- `reference/reference_outline_wrong_vs_right.png`: a part I frame now (with the line) next to the I → II frame
  (without it), on the video's background;
- `reference/reference_hands_close_up.png`: close-ups of the original hands;
- `sheets.csv`.

Then paste:

```
I'm attaching a zip with 12 PNG sprite sheets of a cartoon character (grids/), the original drawings they were
redrawn from (originals/), and three reference images (reference/). Each sheet is 1536 × 1024 with a transparent
background and holds four frames in a 2 × 2 grid (one frame per 768 × 512 cell). originals/ has the same 12
sheets, in the same layout: grids/X.png goes with originals/X_original.png, with the same frame in the same cell.
The character is a cream rectangular card with a lilac edge on the left, a small black beret, orange cheeks and
thin black arms and legs.

Fix two things in every frame of grids/:

1. The black line around the figure. In many frames a thin black line is traced around the outside of the
   whole character's silhouette: along the outer side of the lilac edge, around the top, right side and bottom
   of the card, and as a black ring around each hand. In some frames it goes all the way round, in others only
   part of the way. Remove it everywhere, as shown in reference/reference_outline_wrong_vs_right.png. The figure
   must end like the original and like reference/reference_chase_first_frame.png: the lilac edge, the light cream
   rim of the card and the peach hands go straight to the transparent background, with no dark line. Keep the
   light cream rim, and keep the parts that really are black (beret, eyes, mouth, arms, legs, feet) as they are.

2. The hands. In many frames the hands are just plain round peach circles. Redraw each hand exactly like the
   same hand in the same frame of the original sheet (see also reference/reference_hands_close_up.png): a small
   peach mitten hand with little fingers and a thumb, pointing the same way and in the same gesture (open, fist,
   waving, pointing) as in the original, at the end of the black arm, the same size as now, with no black ring
   around it.

Change nothing else. Keep every frame exactly as it is: the same pose, size, position, colours (cream face
#fbdebb, lilac edge #9e9bfa, orange cheeks #fc9a47, light rim #fcf8e7), beret, face, legs, feet and white motion
lines, and the four frames in the same cells. Don't add anything: no shadow under the character, no glow or
white halo around it, no background. Output each sheet as a PNG, 1536 × 1024, with a transparent background.

Work through all 12 sheets. For every frame, look at its original before you finish it, and keep the hands and
the edge the same from sheet to sheet.

When all 12 are done, give me one zip with grids/ (the 12 sheets, each with exactly the same file name as the
one you got, without "_original") and sheets.csv (unchanged). Before you zip it, open every PNG again to check
it isn't cut short or broken, and redo any that is.
```

If ChatGPT stops partway, reply "continue with the next sheets" until all 12 are done.

When you send me the zip back, I'll check the edges, hands and colours (and put the colours back exactly if they
drift), fit the frames, and show you a before and after before rendering.

## Next: the other parts with the white key

- I → II chase (`W_*`): these are the original drawings, not redraws, so they have no outline and their hands
  are right.
- Part III (`E`–`H`): the round 2 redraws added the same black line around the figure, so they need this fix too. The coda white
  key (`J`) comes from the same round, so check it as well. Their kit uses the same prompt with their own grids and
  originals.
