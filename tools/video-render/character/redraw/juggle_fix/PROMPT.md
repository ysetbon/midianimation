# Fixing the flower-juggling frames (J1–J8, part I, 0:11.6–0:13.7)

The eight juggling frames don't quite match the white key in the rest of part I. Measured on screen in
final 30, with his first frame (16_1) as the reference:

| | First frame 16_1 | Juggling J1–J8 |
|---|---|---|
| Black outline | 4–6 px | 7–9 px (about 1.5× thicker) |
| Card, height : width | 1.38–1.43 : 1 | 1.30–1.33 : 1 (stubbier, 7–11% wider) |
| Legs below the card | 80 px (a quarter of the card's height) | 70 px (shorter, and thicker) |
| Beret width | 0.92–0.95 of the card's width | 0.87–0.91 |

The video already scales each frame so the card is the same height as in his other poses, and draws the soft
ground shadow under his feet. So the drawings themselves need the thinner outline, the slimmer card and the
longer legs; the size on screen follows by itself.

## Files

- `juggle_sheet01.png`, `juggle_sheet02.png`: the two sheets as they are now (J1–J4 and J5–J8, 2 × 2). Send these.
- `reference_partI_sheet01_poses_16_1-16_4.png`: four of his part I poses (16_1 top left) in the look to match. Send this with each sheet.
- `reference_16_1_first_frame.png`: his first frame alone, larger (as he appears in the video, with his shadow).
- `J1.png` … `J8.png`: each juggling frame on its own, if you'd rather fix one at a time.
- `compare_in_video_final30.jpg`: all of them in the video at the same scale, for you to see the difference.

## The prompt (one sheet at a time)

Attach the sheet to fix (`juggle_sheet01.png`, then `juggle_sheet02.png` in a new message) and the reference
sheet, and paste:

```
The first image is a 2 × 2 sheet of four frames of a cartoon character juggling flowers. The second image
shows the same character in four other poses, drawn in the correct style. Redraw the first sheet so the
character matches the second image exactly, while keeping each frame's pose, expression and flowers.

Change only the character's drawing style and proportions, to match the reference:
- Outline: make every black outline thinner, about two thirds as thick as now, the same thin even line as
  in the reference (around the card, the beret, the arms, the hands, the legs and the shoes).
- Card: make the cream card slimmer and taller, the same shape as in the reference (about 1.4 times as tall
  as it is wide), with the same narrow lilac edge on its left side and the same thin white rim inside the
  outline.
- Legs: a little longer and thinner, as in the reference: the legs below the card are about a quarter of
  the card's height, ending in the same small black shoes.
- Beret: the same small black beret as in the reference, almost as wide as the card, with its little stalk.
- Arms and mitten hands: thin black arms and small cream mitten hands with a black outline, as in the
  reference.
- Face: the same eyes, smile and orange cheeks as in the reference, at the same size and place on the card.

Keep everything else in each frame exactly as it is: the same pose, the same direction he faces, the same
expression, the same flowers in the same places (the yellow, orange and cream daisies, the petals and the
little floating flowers), and each frame in its own cell at the same position, standing on the same ground
line.

Do not add anything: no ground shadow, no background, no floor, no text, no lines between the cells. Do
not merge the frames or let them overlap.

Output: one PNG, 1536 × 1024 (landscape), the same 2 × 2 layout, with a transparent background and crisp,
smooth outlines.
```

Save the answers as `juggle_sheet01.png` and `juggle_sheet02.png` (the same names) and send them back to
Claude, who puts them in `redraw/new_frames/`, runs `build/juggle/cut_juggle.py` and rebuilds part I.
If one frame comes out with another pose or face, redo just that sheet.

## Or one frame at a time

Attach `J1.png` (or another) and `reference_16_1_first_frame.png`, and use the same prompt with its first
paragraph replaced by:

```
The first image is one frame of a cartoon character juggling flowers. The second image shows the same
character drawn in the correct style. Redraw the first image so the character matches the second image
exactly, while keeping this frame's pose, expression and flowers.
```

and its last paragraph by `Output: one PNG, 768 × 512 (landscape), the character in the same place, with a
transparent background and crisp, smooth outlines.`
