# Colour audit

Every frame of a final, measured: the background and each character colour, per section.

    python3 scan_colours.py ../../output/etude1_final_40.mp4 final40_colours.json --workers 4    # about 8 min on 4 cores
    python3 summarise.py final40_colours.json data.js                                             # sections, jumps, fades, drifts

`final40_colours.json` is the scan of `etude1_final_40.mp4` (2026-11-15; all 3927 frames). The page made from it
is artifact UpN6rkAByRVt2jR7cctq4L (`data.js` + a sheet of previews every 15 frames + the page). What it found:
no background jumps between sections (fixed in final 40); the coda's planned fade from petrol to purple at
1:52.4–1:53.0; the fade to black at the end takes 3 frames (2:10.40–2:10.47); the dance frames (1:24.4–1:35.0) have
dark grey outlines (#111111–#161616) instead of black (both fixed in final 41). It also flagged the sleep frames' beret line
(Z_5–Z_8) as darker; at full size it is the same green and 2 px as Z_1–Z_4. The scan reads every other pixel, so a 2 px line
can land on its dark middle in one frame and its soft edge in the next: check thin lines at full size.
