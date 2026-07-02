#!/usr/bin/env bash
# Usage: ./scripts/render.sh <scene_file_stem> <SceneClass>
# Example: ./scripts/render.sh context_window ContextWindow
set -euo pipefail
STEM="$1"; CLASS="$2"
manim -r 1920,1080 --fps 30 --format=mp4 --media_dir renders "src/scenes/${STEM}.py" "$CLASS"
MP4=$(find renders/videos -name "${CLASS}.mp4" -path "*1080*" | head -1)
mkdir -p renders/final
cp "$MP4" "renders/final/${STEM}.mp4"
ffmpeg -y -v error -i "renders/final/${STEM}.mp4" \
  -vf "fps=15,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4" \
  -loop 0 "renders/final/${STEM}.gif"
echo "Done: renders/final/${STEM}.mp4 + .gif"
