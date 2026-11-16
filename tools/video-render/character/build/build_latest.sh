#!/bin/bash
# build_latest.sh <outdir> <name.mp4> [reuse_from_dir segment ...]
#
# Builds a final of étude 1 with the settings of the latest final (ethude_1_27's MIDI, sound and timing; see CLAUDE.md),
# from the notes render kept in the repo. Segments named after reuse_from_dir (partI chase partII t2 partIII coda) are
# hard-linked from that earlier build instead of rendered again; build_finals.py skips any segment already in outdir.
#   build_latest.sh /tmp/final44 etude1_final_44.mp4                          # everything rendered (about an hour on CPU)
#   build_latest.sh /tmp/final44 etude1_final_44.mp4 /tmp/final43 partI chase partII t2 coda   # only part III again
# After an interrupted build, delete the half-written segment in outdir before running again.
set -e
cd "$(dirname "$0")/../.."   # tools/video-render
out=$1; name=$2; shift 2
mkdir -p "$out"
if [ $# -gt 0 ]; then
  from=$1; shift
  for seg in "$@"; do ln -f "$from/$seg.mkv" "$out/$seg.mkv"; done
  [ -f "$from/notes_left.json" ] && cp "$from/notes_left.json" "$out/"
fi
TIMEMAP_SHIFT=54.601:0,55.801:0.0179,59.801:0.0179,61.101:0.1607 \
HUGSEQ=119.810:Y_1,120.910:R_4,121.440:U_2,121.930:U_5,123.490:N_3,125.740:M_3,127.740:V_2 \
python3 character/build/build_finals.py character/output/notes_17_ethude1_27.mp4 "$out" \
  --timemap 1.095303:0.127809 --audio character/build/audio/ethude1_27.mp3 --name "$name" --end 130.9
