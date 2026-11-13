# Prompt for ChatGPT: part I white key in the right colours

Attach `redraw_partI_colours.zip` to a new chat. It has:
- `grids/`: the 12 part I sheets the video uses now;
- `reference/colour_reference_chase_first_frame.png`: the white key in the first frame of the I → II chase, the colours to match;
- `reference/colour_swatches.png`: those colours with their codes, next to part I's now;
- `sheets.csv`.

Then paste:

```
I'm attaching a zip with 12 PNG sprite sheets of a cartoon character (grids/) and two reference images
(reference/). Each sheet is 1536 × 1024 with a transparent background and holds four frames in a 2 × 2 grid
(one frame per 768 × 512 cell). The character is a cream rectangular card with a lilac edge on the left, a small
black beret, orange cheeks and thin black arms and legs.

The colours of the character in these sheets are slightly off. Recolour every frame so its colours match the
reference exactly (reference/colour_reference_chase_first_frame.png, and the codes in
reference/colour_swatches.png):
- the cream face of the card: #fbdebb (now it is too peach, #ffdab3);
- the lilac side edge: #9e9bfa (now it is too strong, #8a75fd);
- the orange cheeks: #fc9a47 (now they are too red, #ff8723);
- the light rim around the card: #fcf8e7.
Keep the same soft shading as in the reference: slightly lighter or darker tones of the same colours, never
a different hue. The beret, eyes, mouth, arms, legs and motion lines stay black or white as they are.

Change nothing else. Keep every frame exactly as it is: the same pose, size, position, outlines, face and motion
lines, and the four frames in the same cells. Don't add anything: no shadow under the character, no glow or
white halo around it, no background. Output each sheet as a PNG, 1536 × 1024, with a transparent background.

Work through all 12 sheets. Keep the colours the same from sheet to sheet: compare each sheet with the reference
and with the sheets you've already done.

When all 12 are done, give me one zip with grids/ (the 12 sheets, each with exactly the same file name as the
one you got) and sheets.csv (unchanged). Before you zip it, open every PNG again to check it isn't cut short or
broken, and redo any that is.
```

**Optional:** the reference has no black outline around the card, only the light cream rim; your part I
redraws have a bold black outline. If you want that to match too, add this line before "Change nothing else":
`Also match the card's edge to the reference: a light cream rim, no black outline around the card.`

If ChatGPT stops partway, reply "continue with the next sheets" until all 12 are done.

When you send me the zip back, I'll check every frame's colours against the reference, fit them, and show you a
before and after before rendering.
