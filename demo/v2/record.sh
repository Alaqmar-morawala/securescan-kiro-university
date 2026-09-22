#!/usr/bin/env bash
# Record a REAL end-to-end demo using Chrome DevTools Protocol screencast (no X11).
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
python3 "$OUT/drive.py"
sleep 1
pkill -f "[c]hrome-demo" || true
ls "$FRAMES" | wc -l
echo "frames in $FRAMES"
