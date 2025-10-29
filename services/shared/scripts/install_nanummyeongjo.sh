#!/usr/bin/env bash

set -x
set -e
set -u

mkdir -p ${HOME}/.fonts/
mkdir -p tmp_fonts

wget -O tmp_fonts/NanumMyeongjo-Bold.ttf https://github.com/google/fonts/raw/refs/heads/main/ofl/nanummyeongjo/NanumMyeongjo-Bold.ttf
wget -O tmp_fonts/NanumMyeongjo-Regular.ttf https://github.com/google/fonts/raw/refs/heads/main/ofl/nanummyeongjo/NanumMyeongjo-Regular.ttf
wget -O tmp_fonts/NanumMyeongjo-ExtraBold.ttf https://github.com/google/fonts/raw/refs/heads/main/ofl/nanummyeongjo/NanumMyeongjo-ExtraBold.ttf

cp tmp_fonts/*.ttf ${HOME}/.fonts/

rm -r tmp_fonts
