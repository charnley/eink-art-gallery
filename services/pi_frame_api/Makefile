ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

conda=conda
python=./env/bin/python
pip=pip
package=eink_rpi_api

port=8080
rpi_hostname=

epd_type=BlackRed13

.PHONY: build check clean test

# setup

all: epaper.git env dev-pip

env:
	python3 -m venv ./$@ --system-site-packages
	./$@/bin/python -m pip install --only-binary=:all: -r ./requirements.txt
	make dev-pip python=./$@/bin/python

dev-pip: epaper.git
	${python} -m pip install -e .
	${python} -m pip install -e ../shared/

.PHONY: epaper.git

epaper.git:
	@# NOTE Check if this links the EPD you need
	git clone https://github.com/waveshareteam/e-Paper.git $@ --depth 1 --quiet
	ln -s ${ROOT_DIR}/$@/RaspberryPi_JetsonNano/python/lib/waveshare_epd ./src/waveshare_epd
	ln -s ${ROOT_DIR}/$@/E-paper_Separate_Program/13.3inch_e-Paper_E/RaspberryPi/python/lib/ ./src/waveshare_epd_13in3e

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
