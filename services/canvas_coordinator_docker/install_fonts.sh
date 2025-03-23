#!/usr/bin/env bash

set -x
set -e
set -u

wget -O fira.zip https://github.com/mozilla/Fira/archive/master.zip
unzip fira.zip

# Copy-paste ttf to .fonts so latex can find them

mkdir -p ${HOME}/.fonts/
cp Fira-master/ttf/*.ttf ${HOME}/.fonts/

rm -r Fira-master
rm -r fira.zip
