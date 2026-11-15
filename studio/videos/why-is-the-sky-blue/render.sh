#!/usr/bin/env bash
# Steps 5-6: check, render, normalise to -14 LUFS and encode. Usage: ./render.sh <en|hi|en-short|hi-short> ...
set -euo pipefail
cd "$(dirname "$0")"
for c in "$@"; do
  lang=${c%%-*}; name=final; [[ $c == *-short ]] && name=short
  mkdir -p out/$lang
  (cd composition/$c && npx --yes hyperframes lint >/dev/null && npx --yes hyperframes render --skill=hyperframes --crf 18 --quiet -o ../../out/$lang/_$name.mp4 >/dev/null 2>&1)
  ffmpeg -y -loglevel error -i out/$lang/_$name.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v libx264 -crf 18 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 -movflags +faststart out/$lang/$name.mp4
  rm -f out/$lang/_$name.mp4
  echo "$c -> out/$lang/$name.mp4 $(ffprobe -v error -show_entries format=duration -of csv=p=0 out/$lang/$name.mp4)s"
done
