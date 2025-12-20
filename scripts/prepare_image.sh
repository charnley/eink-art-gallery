#!/bin/bash

# Prepare image to be uploaded to server

set -x
set -e
set -u

res=960x680

convert $1 -resize $res -gravity center -extent $res $1.next.png
