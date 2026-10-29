# Étude 1 character animation (part I and the I → II chase)

The cut-out characters that play over the MuVis render of `17_ethude1.mid`: the
white card character in part I, then the black character chasing him off in the
I → II crossing. `output/etude1_partI_to_II_cocoa_halfshrink.mp4` is the version
chosen on 2026-10-25 as the best so far (0–36.1 s, with the recording).

## The chosen look

| | |
|---|---|
| Notes | hit at 60% of the width (1152 px, render shifted right by 384 px), gone at 25% (480 px) with a 24 px fade |
| Part I background | raspberry rose `#8c3b55`, flat (the MP4 is fed `8b3c55` so it decodes to the closest 8-bit value) |
| Part II background | cocoa umber `#6e4a3c`, flat from 33.11 s |
| Colour change | part II's colour spreads out from the black character as a soft glow, pulses on the 28.55 s stomp, sweeps across from 31.83 s and fills the frame on the 33.11 s chord |
| Character limits | left 35 px; right = nearest note over the next 1.1 s minus 190 px; only the entrance and exit cross the left edge |
| Part I size | scale 2.036 (`SCALE=1.90` × plan `grow` 1.0717): the white body is about 346 px tall |
| Crossing camera | pulls back to 83% while the black one creeps in (26.35–27.25 s, `S2=1.693`), moves back in after the white one runs off (32.47–33.11 s) until the black one stands about 475 px tall, as tall as the white one in part I |
| Timing | poses change on the note onsets (about 0.13–0.4 s apart), part I on a 0.2 s grid |

Other versions made along the way: the camera pulled back to 66% (`S2=1.35`),
no camera move at all (`NOSHRINK=1`, both at full size the whole time) and a
rust terracotta `#8a4336` part II. The 16 candidate colours are compared in
the Part II Palette artifact.

## Sheets (`sheets/`)

All transparent 4×4 sheets, poses read left to right, top to bottom.

- `partI_17.png`, `partI_18.png`, `partI_19.png`: part I (burst and rest, warming up, shimmer). Part I still uses this older, squarer white figure, so he changes shape at 26.2 s. Redrawing these three as the tall card would fix that.
- `white_chase.webp`: the white one in the chase, the tall card. 1 wave, 2 stroll, 3 startled, 4 scared, 5–8 run, 9 skid, 10 leap, 11 land, 12 pant, 13 look back, 14 dash ready, 15 dash, 16 blur.
- `black_chase.png`: the black one. 1–4 creep (3 shush), 5 stomp, 6–9 run, 10 lunge, 11 grab at nothing, 12 hands on hips, 13 glare, 14 anger mark, 15–16 arms crossed.

## The whole video

`build/` makes both final videos (A, the new export; B, the patched recording) from a notes render, with every part and crossing in its chosen look: see `build/README.md`.

## Re-making it

Put two files in `work/` (ignored by git): `etude1_final_v3.mp4`, the full
render with the recording (`render.js`), and, after the first step,
part I's lossless file.

```sh
# part I (0-26.2 s): cut the sheets, then render (exact colour; drop LOSSLESS and use BGCOLOR=8b3c55 for an MP4)
cd partI && python3 cut2.py
SPRITES=$PWD SHIFT=384 SCALE=1.90 PLAN=$PWD/plan_partI.json FLAT=1 LOSSLESS=1 BGCOLOR=8c3b55 \
  python3 anim.py ../work/etude1_final_v3.mp4 ../work/etude1_partI_raspberry_plan_lossless.mkv

# the crossing and the joined video (defaults are the chosen look)
cd ../crossing && ./encode_all.sh            # S2=1.35 or NOSHRINK=1 or BG2=<hex> for the other versions
```

`encode_all.sh` writes `etude1_crossing_I_II.mp4`, `etude1_crossing_I_II_lossless.mkv`
and `etude1_partI_to_II.mp4` to `work/`. Both steps reproduce the saved output
pixel for pixel.

- **New sheet:** to swap in a new chase sheet, replace the file in `sheets/`, delete `crossing/chase_sprites.npz` and run again. Each sheet is scaled so the white body matches part I's height, and the poses stand on their feet.
- **Choreography:** the timing lives in `crossing/chase.py` (`WHITE` and `BLACK`: time, pose, body centre x, height in the air, mirrored, may leave the frame).
- **Note positions:** `partI/notes_partI.json` and `crossing/notes_crossing.json` hold the leftmost note pixel per frame (after the 384 px shift), which the right limit follows.
