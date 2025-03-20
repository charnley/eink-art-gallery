ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

conda=conda
python=./env/bin/python
pip=pip
package=pi_server

.PHONY: build check clean test

# setup

art: env

all: epaper.git env dev-pip

env:
	python3 -m venv ./$@
	./$@/bin/python -m pip install -r ./requirements.txt
	make dev-pip python=./$@/bin/python

dev-pip:
	${python} -m pip install -e .

epaper.git:
	git clone https://github.com/waveshareteam/e-Paper.git $@ --depth 1 --quiet
	ln -s ${ROOT_DIR}/$@/RaspberryPi_JetsonNano/python/lib/waveshare_epd ./src/waveshare_epd

# development

todo:
	grep "# TODO" */*.py | sed -e 's/    //g' | sed -e 's/# TODO//'

# Service

start:
	${python} -m uvicorn picture_api:app \
		--host 0.0.0.0 \
		--port 8080 \
		--log-config=logging.yaml

# clean

clean:
	rm -r build *.pyc __pycache__ _tmp_* *.egg-info
