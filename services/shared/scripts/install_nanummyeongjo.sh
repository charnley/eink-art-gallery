#!/usr/bin/env bash

set -x
set -e
set -u

wget -O nanum.zip https://github.com/naver/nanumfont/archive/refs/heads/master.zip
unzip nanum.zip

mkdir -p "${HOME}/.fonts/"
find nanumfont-master -type f -iname "NanumMyeongjo*.ttf" -exec cp {} "${HOME}/.fonts/" \;

rm -rf nanumfont-master
rm -f nanum.zip
