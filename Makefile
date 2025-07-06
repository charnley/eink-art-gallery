.PHONY: build check clean test

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
python=python

refill_server=
push_server=

# Services

setup-pre-commit:
	${python} -m pre_commit install

pre-commit-all:
	${python} -m pre_commit run --all-files

format: pre-commit-all

# start

start-art-jupyter:
	HF_HOME=${ROOT_DIR}/models cd ./services/desktop_server/ && make start-jupyter

start-art-service:
	test -z "${refill_server}"
	cd ./services/desktop_server/ && make start-refill refill_server=${refill_server}

clean:
	rm -r build *.pyc __pycache__ _tmp_* *.egg-info

clean-env:
	rm -fr ./services/*/env
