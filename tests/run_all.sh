#!/usr/bin/env bash
# Runs every check against the app. Usage:
#   GUIDE_TEXT=/path/to/your-guide-text.txt [GUIDE_PHOTOS=/folder/of/photo-page-screenshots] tests/run_all.sh
# The guide's text and photos are not in this repo (they're from the book); point at your own copies.
cd "$(dirname "$0")/.." || exit 1
APP="$PWD/index.html"; OUT="$(mktemp -d)"; TEXT="${GUIDE_TEXT:?Set GUIDE_TEXT to a text file of the chapter}"
fail=0
for t in run2 coffee2 search2 openlist gest3 voice4 audio2b shots jump parts banner repeat maptest backup photopanel; do
  res=$(timeout 240 python3 "tests/$t.py" "$APP" "$OUT" "$TEXT" 2>&1)
  if echo "$res" | grep -qiE "Traceback|errors \[[^]]"; then echo "FAIL  $t"; echo "$res" | tail -5; fail=1; else echo "ok    $t"; fi
done
echo "Screenshots: $OUT"; exit $fail
