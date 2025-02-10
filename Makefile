ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

.PHONY: build check clean test

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
	cd ./services/desktop_server/ && make start-art-service-push
	cd ./services/desktop_server/ && make start-art-service-refill

clean:
	rm -r build *.pyc __pycache__ _tmp_* *.egg-info

clean-env:
	rm -fr ./services/*/env
