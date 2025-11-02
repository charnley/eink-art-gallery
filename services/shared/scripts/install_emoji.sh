#!/usr/bin/env bash

set -x
set -e
set -u

mkdir -p ~/.fonts
mkdir -p tmp_fonts

wget -O tmp_fonts/seguiemj-1.35-flat.ttf https://github.com/popemkt/segoe-ui-emoji/raw/refs/heads/main/seguiemj-1.35-flat.ttf
find tmp_fonts -type f -iname "*.ttf" -exec cp {} ~/.fonts/ \;

rm -r tmp_fonts
