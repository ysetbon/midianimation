# Prompt for ChatGPT: part I without ground shadows (optional)

The shadows are already fixed in the video: the redraws' shadows are replaced with clean soft ovals
(`build/hd/shadow_fix.py`). Use this only if you also want the drawings themselves without a shadow. Then
nothing is left to clean, and the clean ovals go under them.

Attach `redraw_partI_sheets.zip` (the 12 part I sheets you got back from ChatGPT, in `grids/`, plus
`sheets.csv`) to a new chat and paste:

```
I'm attaching a zip with 12 PNG sprite sheets of a cartoon character for a music video. Each sheet is
1536 × 1024 with a transparent background and holds four frames in a 2 × 2 grid (one frame per 768 × 512 cell).
The character is a cream rectangular card with a lilac edge on the left, a small black beret, orange cheeks
and thin black arms and legs.

Under the character in most frames there is a grey oval shadow on the ground. Please remove only that shadow:
the grey oval and its light outline, so the background under the feet is fully transparent.

Change nothing else. Keep every frame exactly as it is: the same pose, size, position, colours, outlines, feet,
legs and the white motion lines. Don't add anything, don't move anything, and keep the four frames in the same
cells. Output each sheet as a PNG, 1536 × 1024, with a transparent background.

When all 12 are done, give me one zip with grids/ (the 12 sheets, each with exactly the same file name as the
one you got) and sheets.csv (unchanged). Before you zip it, open every PNG again to check it isn't cut short or
broken, and redo any that is.
```

If ChatGPT stops partway, reply "continue with the next sheets" until all 12 are done.
