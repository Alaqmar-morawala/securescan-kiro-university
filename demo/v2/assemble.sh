#!/usr/bin/env bash
# Assemble captured frames into the final demo video (even dims for libx264).
set -e
cd /home/alaqmar/pentest001/challenge/demo/v2
awk '/^duration/{s+=$2} END{printf "timeline: %.1fs\n", s}' frames/frames.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i frames/frames.txt \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
  -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p -r 30 \
  -movflags +faststart securescan-demo-real.mp4
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 securescan-demo-real.mp4
