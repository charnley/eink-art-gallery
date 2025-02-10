ROOT_DIR:=$(realpath $(shell dirname $(firstword $(MAKEFILE_LIST))))
GIT_ROOT:=$(shell git rev-parse --show-toplevel)


package=desktop_server
env=env
python=${env}/bin/python
model_dir=${GIT_ROOT}/models

all: ${env}

## Env

${env}:
	uv venv ${env} --python 3.12
	uv pip install -r requirements.txt --python ./${env}/bin/python
	uv pip install -e . --python ./${env}/bin/python

## Python

start-art-service-push:
	HF_HOME=${GIT_ROOT}/models \
	${python} -m art_service --push --prompt \"$$(shuf -n 1 ${ROOT_DIR}/assets/random_artists.txt)\" --use-red

start-art-service-refill:
	HF_HOME=${GIT_ROOT}/models \
	${python} -m art_service --refill

start-art-api:
	HF_HOME=${GIT_ROOT}/models \
	${python} -m uvicorn art_api:app \
		--host 0.0.0.0 \
		--port 8080 \
		--log-config=${GIT_ROOT}/logging.yaml


start:
	python -m ${package}
