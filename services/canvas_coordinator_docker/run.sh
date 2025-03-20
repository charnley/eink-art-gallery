#!/usr/bin/sh

echo "Hello world!"

ls -lh /data

which python
python -m canvasserver --start --options /data/options.json
