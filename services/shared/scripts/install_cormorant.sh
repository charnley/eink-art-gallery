#!/usr/bin/env bash

set -x
set -e
set -u

mkdir -p ~/.fonts
mkdir -p tmp_fonts

wget -O tmp_fonts/fonts.zip https://github.com/CatharsisFonts/Cormorant/releases/download/v4.002/Cormorant_Essentials_v4.002.zip
cd tmp_fonts && unzip fonts.zip
cd ..
find tmp_fonts -type f -iname "*.otf" -exec cp {} ~/.fonts/ \;

rm -r tmp_fonts
