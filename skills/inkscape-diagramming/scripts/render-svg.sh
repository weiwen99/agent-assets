#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s INPUT.svg [OUTPUT.png] [DPI]\n' "$0" >&2
  exit 64
}

[[ $# -ge 1 && $# -le 3 ]] || usage

svg=$1
[[ -f "$svg" && "$svg" == *.svg ]] || {
  printf 'Input must be an existing .svg file: %s\n' "$svg" >&2
  exit 66
}

png=${2:-${svg%.svg}.png}
dpi=${3:-192}
[[ "$png" == *.png ]] || {
  printf 'Output must end in .png: %s\n' "$png" >&2
  exit 64
}
[[ "$dpi" =~ ^[1-9][0-9]*$ ]] || {
  printf 'DPI must be a positive integer: %s\n' "$dpi" >&2
  exit 64
}
command -v inkscape >/dev/null 2>&1 || {
  printf 'inkscape is required but was not found on PATH\n' >&2
  exit 69
}

mkdir -p "$(dirname "$png")"
inkscape "$svg" \
  --export-area-page \
  --export-background='#ffffff' \
  --export-background-opacity=255 \
  --export-dpi="$dpi" \
  --export-filename="$png"

[[ -s "$png" ]] || {
  printf 'Inkscape did not create a non-empty PNG: %s\n' "$png" >&2
  exit 74
}
printf 'Rendered %s -> %s at %s dpi\n' "$svg" "$png" "$dpi"
