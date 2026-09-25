#!/usr/bin/env bash
# Record the REAL-engine demo (CDP screencast) and assemble the final video.
# Prereqs: ZAP daemon up (manage.py zap up), vuln_target on 8473, runserver
# on 8472 with SECURESCAN_MOCK=0 SECURESCAN_ALLOW_PRIVATE_TARGETS=1.
set -e
W=1280; H=800
OUT=/home/alaqmar/pentest001/challenge/demo/v2
FRAMES=$OUT/frames
pkill -f "[c]hrome-demo" 2>/dev/null || true
rm -rf "$FRAMES" "$OUT/chrome.log"
mkdir -p "$FRAMES"
chromium \
  --user-data-dir=/tmp/chrome-demo \
  --no-first-run --no-default-browser-check --disable-infobars \
  --disable-features=Translate,MediaRouter --disable-sync \
  --window-size=${W},${H} --window-position=0,0 \
  --remote-debugging-port=9222 --remote-allow-origins=* \
  --no-sandbox --disable-gpu --hide-scrollbars \
  about:blank >"$OUT/chrome.log" 2>&1 &
sleep 5
python3 "$OUT/drive_real.py"
sleep 1
pkill -f "[c]hrome-demo" || true
echo "frames: $(ls "$FRAMES" | grep -c jpg)"
cd "$OUT"
ffmpeg -y -loglevel error -f concat -safe 0 -i frames/frames.txt \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
  -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p -r 30 \
  -movflags +faststart securescan-demo-real-engine.mp4
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 securescan-demo-real-engine.mp4
