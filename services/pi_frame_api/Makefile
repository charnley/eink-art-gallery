ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

conda=conda
python=./env/bin/python
pip=pip
package=eink_rpi_api

port=8080
rpi_hostname=

.PHONY: build check clean test

# setup

all: epaper.git env dev-pip

env:
	python3 -m venv ./$@
	./$@/bin/python -m pip install -r ./requirements.txt
	make dev-pip python=./$@/bin/python

dev-pip: epaper.git
	${python} -m pip install -e .
	${python} -m pip install -e ../shared/

epaper.git:
	git clone https://github.com/waveshareteam/e-Paper.git $@ --depth 1 --quiet
	ln -s ${ROOT_DIR}/$@/RaspberryPi_JetsonNano/python/lib/waveshare_epd ./src/waveshare_epd

fonts:
	mkdir -p ${HOME}/.fonts/
	mkdir $@
	cd $@ && wget -O fira.zip https://github.com/mozilla/Fira/archive/master.zip
	cd $@ && unzip fira.zip
	cp $@/Fira-master/ttf/*.ttf ${HOME}/.fonts/
	rm -r $@
	rm -rf ~/.cache/matplotlib/

# start

dev:
	${python} -m ${package} --start --port ${port} --reload --logging-config ./logging_config.yaml

start:
	${python} -m ${package} --start --port ${port} --logging-config ./logging_config.yaml

# development

test:
	${python} -m pytest ./tests/

todo:
	grep "# TODO" */*.py | sed -e 's/    //g' | sed -e 's/# TODO//'

# clean

clean:
	rm -r build *.pyc __pycache__ _tmp_* *.egg-info
