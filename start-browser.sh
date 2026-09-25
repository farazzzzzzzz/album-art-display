#!/bin/sh
export DISPLAY="${DISPLAY:-:0}"
export XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"

exec /usr/bin/chromium \
  --kiosk \
  --no-first-run \
  --no-default-browser-check \
  --disable-pings \
  --media-router=0 \
  --disable-dev-shm-usage \
  --enable-gpu-rasterization \
  --use-angle=gles \
  --noerrdialogs \
  --disable-session-crashed-bubble \
  --user-data-dir="$HOME/.config/album-display/chromium-kiosk" \
  "file://$HOME/.config/album-display/index.html"
