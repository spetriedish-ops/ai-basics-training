#!/usr/bin/env python3
"""Interleave frames from 3 seed renders into one 'boiling line' video.

Usage: python3 scripts/interleave.py <stem> <SceneClass> [--hold N] [--src DIR]
Expects renders/boil_s{1,2,3}/videos/<stem>/*/SceneClass.mp4
Writes renders/final/<stem>.mp4 and .gif
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stem")
    ap.add_argument("cls")
    ap.add_argument("--hold", type=int, default=5,
                    help="frames per seed before switching (5 @ 30fps = 6Hz boil)")
    ap.add_argument("--fps", type=int, default=30)
    args = ap.parse_args()

    vids = []
    for s in (1, 2, 3):
        hits = sorted(Path(f"renders/boil_s{s}").rglob(f"{args.cls}.mp4"))
        if not hits:
            sys.exit(f"missing render for seed {s}")
        vids.append(hits[0])

    work = Path("renders/boil_frames")
    if work.exists():
        shutil.rmtree(work)
    for k, vid in enumerate(vids):
        out = work / f"k{k}"
        out.mkdir(parents=True)
        run(["ffmpeg", "-v", "error", "-i", str(vid),
             "-vf", f"select='eq(mod(floor(n/{args.hold}),3),{k})'",
             "-vsync", "vfr", str(out / "%05d.png")])

    pools = [sorted((work / f"k{k}").glob("*.png")) for k in range(3)]
    seq = work / "seq"
    seq.mkdir()
    idx = [0, 0, 0]
    i = 0
    while True:
        k = (i // args.hold) % 3
        if idx[k] >= len(pools[k]):
            break
        (seq / f"{i:05d}.png").symlink_to(pools[k][idx[k]].resolve())
        idx[k] += 1
        i += 1

    final = Path("renders/final")
    final.mkdir(parents=True, exist_ok=True)
    mp4 = final / f"{args.stem}.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-framerate", str(args.fps),
         "-i", str(seq / "%05d.png"), "-c:v", "libx264",
         "-pix_fmt", "yuv420p", "-crf", "18", str(mp4)])
    run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4),
         "-vf", ("fps=15,scale=960:-1:flags=lanczos,split[s0][s1];"
                 "[s0]palettegen=max_colors=128[p];"
                 "[s1][p]paletteuse=dither=bayer:bayer_scale=4"),
         "-loop", "0", str(final / f"{args.stem}.gif")])
    shutil.rmtree(work)
    print(f"Done: {mp4} + gif  ({i} frames)")


if __name__ == "__main__":
    main()
