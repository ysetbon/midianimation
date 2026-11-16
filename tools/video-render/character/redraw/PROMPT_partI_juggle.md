# Prompt for ChatGPT: the white key juggles flowers (0:10.9–0:12.9)

At 0:10.9–0:12.9 the white key now plays his dizzy frames, shaking with spiral eyes, which don't fit the music
there: a run of falling A's (one note every 0.15 s), then two loud chords (0:12.07 and 0:12.21). This new sequence
makes him juggle three little flowers instead, sweet and innocent, with small flowers and petals floating around
him: a toss on each note of the run, a big toss on the first chord, the catch on the second, a shy bow, and then he
sits down at 0:12.89 as he does now.

Attach `new_frames_partI_juggle.zip` to a new chat. It has:
- `reference/reference_character_part_I.png`: four of his part I frames (his look, size and style);
- `reference/video_frame_0-10.6_before.png`, `video_frame_0-12.0_now_spiral_eyes.png` and
  `video_frame_0-13.0_after.png`: the video just before, the frames being replaced, and just after (where he sits);
- `storyboard.csv`: the 8 new frames, which sheet and cell each goes in, and the note each one lands on.

Then paste:

```
I'm attaching a zip with reference images of a cartoon character (reference/) and a storyboard (storyboard.csv).
The character is a cream rectangular card with a lilac edge on the left, a small black beret, black dot eyes,
orange cheeks, a small smile, thin black arms and legs and small peach mitten hands, with a thin black stroke all
the way round the figure, flat colours and soft shading, exactly as in reference/reference_character_part_I.png.

Draw 8 new frames of this character juggling flowers, as two sprite sheets: juggle_sheet01.png and juggle_sheet02.png.
Each sheet is a PNG, 1536 × 1024, with a transparent background, and holds four frames in a 2 × 2 grid (one frame
per 768 × 512 cell). storyboard.csv says which frame goes in which cell and what happens in it. The mood is
innocent and sweet: he holds three little flowers, tosses them up one by one, juggles them in a gentle cascade,
tosses all three up high, catches them (one in each hand, one landing on his beret like a hat flower) and takes a
shy little bow, with small flowers and petals floating softly around him.

For every frame:
- It is the same character as in the reference: the same design, proportions, colours (cream face #fbdebb, lilac
  edge #9e9bfa, orange cheeks #fc9a47, light rim #fcf8e7), black stroke, mitten hands and style. Only his pose,
  his face and the flowers change. His face is innocent and happy: dot eyes (wide and shining, or closed happy
  arcs), a sweet smile, rosy cheeks; never spirals.
- The same size as in the reference: he is as tall as there, standing at the bottom of his cell, his feet about
  26 px above the cell's lower edge. The flowers fly in the free space above him, never outside his own cell.
- The juggled flowers: three little daisy-like flowers with round petals and a small centre, one yellow
  (#f9c440), one orange (#ee7a2b) and one cream (#f3dcc4), like the notes in the video, each with the same thin
  black stroke. Each flower keeps its colour in every frame.
- Around him: a few small floating flowers and loose petals in the same colours (plus a soft pink), more of them
  on the big toss and the catch, as the storyboard says, in the same style with a thin black outline.
- Don't add anything else: no shadow under him, no floor, no glow, no background, no text, no lines between the
  cells.

Keep the character the same from frame to frame and between the two sheets, so the frames play smoothly one after
another: compare each new frame with the reference and with the frames you've already drawn.

When both sheets are done, give me one zip with the two PNGs and storyboard.csv (unchanged). Before you zip it,
open every PNG again to check it isn't cut short or broken, and redo any that is.
```

If ChatGPT stops partway, reply "continue with the next sheet".

When you send me the zip back, I'll cut out the frames, put the stroke colours and the soft ground shadow on like
his other part I frames, time them to the notes in the storyboard, and show you a preview before rendering.
