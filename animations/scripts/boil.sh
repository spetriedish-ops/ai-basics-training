#!/usr/bin/env bash
# Full scribble/boil pipeline: 3 seed renders + frame interleave.
# Usage: ./scripts/boil.sh <scene_file_stem> <SceneClass>
set -euo pipefail
STEM="$1"; CLASS="$2"
for s in 1 2 3; do
  echo "=== seed $s ==="
  SCRIBBLE_SEED=$s manim -r 1920,1080 --fps 30 --format=mp4 \
    --media_dir "renders/boil_s$s" "src/scenes/${STEM}.py" "$CLASS"
done
python3 scripts/interleave.py "$STEM" "$CLASS"
