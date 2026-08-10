#!/usr/bin/env bash
# Boil + verify + package the preamble clips. Run from animations/.
set -euo pipefail
PAIRS=(
  "preamble01:Preamble01:P01-the-algorithm-van"
  "preamble02:Preamble02:P02-fraud-flag"
  "preamble03:Preamble03:P03-decades-road"
  "preamble04:Preamble04:P04-factory-export-gate"
  "preamble05:Preamble05:P05-next-years-truck"
  "preamble06:Preamble06:P06-movie-vs-job"
  "preamble07a:Preamble07a:P07a-tedium-hauled-away"
  "preamble07b:Preamble07b:P07b-the-garden"
  "preamble07c:Preamble07c:P07c-breakthroughs"
  "preamble08a:Preamble08a:P08a-the-worker"
  "preamble08b:Preamble08b:P08b-the-benefits-stack"
  "preamble08c:Preamble08c:P08c-fuel-lozenge"
  "preamble09:Preamble09:P09-seat-and-vibe-shed"
  "preamble10:Preamble10:P10-specialist-parade"
  "preamble11:Preamble11:P11-series-title"
)
CLASSES=""
for pair in "${PAIRS[@]}"; do IFS=: read -r _ cls _ <<< "$pair"; CLASSES="$CLASSES $cls"; done
for s in 1 2 3; do
  SCRIBBLE_SEED=$s manim -r 1920,1080 --fps 30 --format=mp4 \
    --media_dir "renders/boil_s$s" src/scenes/preamble.py $CLASSES
done
mkdir -p deliverables/preamble
rm -f deliverables/preamble/P07-the-upside.mp4 deliverables/preamble/P08-the-ledger.mp4
for pair in "${PAIRS[@]}"; do
  IFS=: read -r stem cls name <<< "$pair"
  python3 scripts/interleave.py "$stem" "$cls"
  python3 scripts/verify.py "renders/final/$stem.mp4"
  cp "renders/final/$stem.mp4" "deliverables/preamble/$name.mp4"
done
echo PREAMBLE_OK
