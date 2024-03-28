conda=conda
python=python
pip=pip
module=eink_picture_generator
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

compile: env_esphome install_custom_esphome compile
env_esphome:
	python -m venv ./$@
	./$@/bin/python -m pip install -r ./requirements.txt
	make dev-pip python=./$@/bin/python

dev-pip:
	${python} -m pip install -e .

install_custom_esphome:
	cd ../../../esphome
	${python} setup.py install
	cd ../eink_picture_generator/src/esphome

compile: env_esphome install_custom_esphome
	esphome compile ./config.yaml

run: env_esphome install_custom_esphome
	esphome run ./config.yaml

clean:
	rm -r build *.pyc __pycache__ _tmp_* *.egg-info

clean-env:
	rm -fr ./esp_home