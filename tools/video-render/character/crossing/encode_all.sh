#!/bin/bash
# Render the I -> II crossing (26.2-36.1 s, lossless) and make the delivered files from it.
# Needs in $WORK (default: ../work): etude1_final_v3.mp4 (the full MuVis render with the
# recording) and etude1_partI_raspberry_plan_lossless.mkv (part I, from ../partI/anim.py).
# Defaults are the chosen look: cocoa umber, camera pulls back to 83% (S2=1.693).
#   BG2=6e4a3c S2=1.693 ./encode_all.sh          NOSHRINK=1 for full size throughout
set -e
D=$(cd "$(dirname "$0")" && pwd); WORK=${WORK:-$D/../work}; cd "$WORK"
SRC=etude1_final_v3.mp4; export SRC="$WORK/$SRC"
V="-c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -movflags +faststart"
[ -f "$D/chase_sprites.npz" ] || python3 "$D/cut3.py"
LOSSLESS=1 python3 "$D/chase.py" "$SRC" crossing_long_lossless.mkv 26.2 36.1333 2>&1 | grep -v "Broken pipe\|Error muxing\|trailer" || true
# the crossing alone (26.2-33.1 s), standard and exact-colour
ffmpeg -y -v error -i crossing_long_lossless.mkv -ss 26.2 -t 6.9333 -i "$SRC" -filter_complex "[0:v]trim=start_frame=0:end_frame=208,setpts=PTS-STARTPTS,scale=out_color_matrix=bt709:out_range=tv[v]" -map "[v]" -map 1:a $V -c:a aac -b:a 192k -shortest etude1_crossing_I_II.mp4
ffmpeg -y -v error -i crossing_long_lossless.mkv -ss 26.2 -t 6.9333 -i "$SRC" -filter_complex "[0:v]trim=start_frame=0:end_frame=208,setpts=PTS-STARTPTS[v]" -map "[v]" -map 1:a -c:v libx264rgb -qp 0 -preset medium -pix_fmt rgb24 -c:a aac -b:a 192k -shortest etude1_crossing_I_II_lossless.mkv
# part I (786 frames) + the crossing and 3 s of part II, with the recording
ffmpeg -y -v error -i etude1_partI_raspberry_plan_lossless.mkv -i crossing_long_lossless.mkv -t 36.1 -i "$SRC" -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0,scale=out_color_matrix=bt709:out_range=tv[v]" -map "[v]" -map 2:a $V -c:a aac -b:a 192k -shortest etude1_partI_to_II.mp4
echo "written to $WORK"
