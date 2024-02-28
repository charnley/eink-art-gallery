conda=conda
python=python
pip=pip
module=eink_picture_generator

.PHONY: build check clean test

# setup

art: env dev-pip

picture: env_picture dev-pip

env_art:
	${conda} env create -f environment.yaml -p ./env --quiet
	make dev-pip python=./$@/bin/python

env_picture:
	python3 -m venv ./$@
	./$@/bin/python -m pip install -r ./requirements_picture.txt
	make dev-pip python=./$@/bin/python

dev-pip:
	${python} -m pip install -e .

# development

todo:
	grep "# TODO" */*.py | sed -e 's/    //g' | sed -e 's/# TODO//'

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

# test-ipynb:
# 	jupytext --output _tmp_script.py notebooks/example_demo.ipynb
# 	${python} _tmp_script.py

types:
	${python} -m monkeytype run `which pytest` ./tests/
	${python} -m monkeytype list-modules | grep ${module} | xargs -n1 monkeytype apply

# start

start-jupyter:
	${python} -m jupyter lab

start-picture-api:
	${python} -m uvicorn picture_api:app --log-config=logging.yaml --port 80

# clean

clean:
	rm -r build *.pyc __pycache__ _tmp_* *.egg-info

clean-env:
	rm -fr ./env_art ./env_picture
