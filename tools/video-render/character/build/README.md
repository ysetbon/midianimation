# Building the étude's final videos

Everything after the notes render: each part's character, colours and camera, and both soundtracks.

1. Render the notes (fast on a GPU, about 1½ minutes):

   ```
   cd tools/video-render
   PITCH_PAD=2,2 HANDS=hands/17_ethude1.json SECTIONS=sections/17_ethude1.json \
   DURATION=122.136 AUDIO_SYNC=1.0434:0.04 node render.js midi/17_ethude1_3removed.mid out 11_sections
   ```

   It must report `3664 frames`. `PITCH_PAD=2,2` leaves the same small room above the highest note
   (F#6) and below the lowest (B0), so both sit just inside the frame; the highest notes still jump out
   of it in part I, as chosen. `8,2` keeps every jump inside instead; leaving it out gives the old framing.

2. Build both finals from it:

   ```
   pip install -r character/build/requirements.txt
   python character/build/build_finals.py out/11_sections.mp4 out/finals
   ```

   This writes `etude1_final_A_new_export.mp4` (the new export) and `etude1_final_B_patched.mp4`
   (the original recording, patched where the three notes were removed) to `out/finals`. Each part is
   kept there as it's made (`partI.mkv` … `coda.mkv`) and skipped on a rerun; add `--force` to remake
   them all, for example after a new notes render.

| Step | Script | Frames |
| --- | --- | --- |
| Part I, raspberry rose | `partI/anim.py` | 786 |
| I → II crossing, cocoa umber, camera to 83% | `chase/chase.py`, then `chase/renote.py` for part II's note colours | 208 |
| Part II | `partII/partII.py` (note colours from `partII/recolor.py`) | 1000 |
| II → III crossing, the piano and the shine | `t2/t2.py` | 237 |
| Part III | `partIII/partIII.py` | 846 |
| Coda | `coda/coda.py` (vanish line from `coda/crop.py`) | 587 |

`audio/` holds the two soundtracks, already lined up with the video (24-bit FLAC).
Needs Python 3 with numpy and scipy, and ffmpeg.

## The 105 BPM version

Your hand files edited for playability, played at 105 BPM (`ethude1_20_hardlimiter.mp3`). The characters,
camera and crossings keep their choreography, slowed to the new tempo through `timemap.py`, and the
rocking and fade after the last note end exactly at 2:11.5, where the video and sound stop.

```
PITCH_PAD=2,2 HANDS=hands/17_ethude1_105.json SECTIONS=sections/17_ethude1.json \
DURATION=134.857 AUDIO_SYNC=1.142857:-0.003 node render.js midi/17_ethude1_105.mid out105 11_sections
python character/build/build_finals.py out105/11_sections.mp4 out105/finals --force \
  --timemap 1.095303:-0.046812 --audio <path to ethude1_20_hardlimiter.mp3> --name etude1_final_105bpm.mp4 --end 131.5
```
