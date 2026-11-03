#!/bin/sh
# Soi nhanh: render still cho mọi shot của một khối.
#   sh tools/render_stills.sh <khoi> <thư mục ra> [mốc giây, mặc định 1,0.5d,0.95d]
# Mốc mặc định: 1 s, giữa shot và gần cuối (đọc DURATION trong shots/*.js).
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)
BLOCK=$1; OUT=$2; TIMES=$3
python "$ROOT/tools/build_shots.py" "$BLOCK" >/dev/null
for js in "$ROOT/$BLOCK"/shots/*.js; do
  name=$(basename "$js" .js)
  if [ -z "$TIMES" ]; then
    d=$(grep -o 'duration: *[0-9.]*' "$js" | head -1 | grep -o '[0-9.]*$')
    ts=$(python -c "d=$d; print(f'1,{d*0.5:.2f},{d*0.95:.2f}')")
  else ts=$TIMES; fi
  node "$ROOT/../tools/kit/dung-trang.mjs" "$ROOT/$BLOCK/$name.html" --stills "$ts" --out-dir "$OUT/$name" 2>&1 | head -1
done
