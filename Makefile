conda=conda
python=python
pip=./env/bin/pip
module=eink_picture_generator

.PHONY: build check clean test

all: env dev-pip

todo:
	grep "# TODO" */*.py | sed -e 's/    //g' | sed -e 's/# TODO//'

env:
	${conda} env create -f environment.yaml -p ./env --quiet

dev-pip: env
	${pip} install -e .

conda-install-build:
	${conda} install conda-build -c conda-forge -y

setup-pre-commit:
	${python} -m pre_commit install

pre-commit-all:
	${python} -m pre_commit run --all-files

format: pre-commit-all

test: test-unit

test-unit:
	${python} -m pytest --basetemp=".pytest" -vrs tests/

start-jupyter:
	${python} -m jupyter lab

# test-ipynb:
# 	jupytext --output _tmp_script.py notebooks/example_demo.ipynb
# 	${python} _tmp_script.py

types:
	${python} -m monkeytype run `which pytest` ./tests/
	${python} -m monkeytype list-modules | grep ${module} | xargs -n1 monkeytype apply

clean:
	rm -r build *.pyc __pycache__ _tmp_* *.egg-info

clean_env:
	rm -fr ./env

