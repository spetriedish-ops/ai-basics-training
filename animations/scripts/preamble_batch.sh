#!/usr/bin/env bash
# Boil + verify + package the 11 preamble clips. Run from animations/.
set -euo pipefail
CLASSES=""; for i in $(seq -w 1 11); do CLASSES="$CLASSES Preamble$i"; done
for s in 1 2 3; do
  SCRIBBLE_SEED=$s manim -r 1920,1080 --fps 30 --format=mp4 \
    --media_dir "renders/boil_s$s" src/scenes/preamble.py $CLASSES
done
for i in $(seq -w 1 11); do
  python3 scripts/interleave.py "preamble$i" "Preamble$i"
  python3 scripts/verify.py "renders/final/preamble$i.mp4"
done
mkdir -p deliverables/preamble
declare -a NAMES=(x the-algorithm-van fraud-flag decades-road \
  factory-export-gate next-years-truck movie-vs-job the-upside the-ledger \
  seat-and-vibe-shed specialist-parade series-title)
for i in $(seq 1 11); do
  ii=$(printf "%02d" "$i")
  cp "renders/final/preamble$ii.mp4" \
     "deliverables/preamble/P$ii-${NAMES[$i]}.mp4"
done
echo PREAMBLE_OK
