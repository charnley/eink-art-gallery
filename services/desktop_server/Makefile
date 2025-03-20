ROOT_DIR:=$(realpath $(shell dirname $(firstword $(MAKEFILE_LIST))))
GIT_ROOT:=$(shell git rev-parse --show-toplevel)

package=desktop_server
env=env
python=${env}/bin/python
model_dir=${GIT_ROOT}/models

refill_server=
push_server=

all: ${env}

## Env

${env}:
	uv venv ${env} --python 3.12
	uv pip install -r requirements.txt --python ./${env}/bin/python
	uv pip install -e . --python ./${env}/bin/python
	uv pip install -e ../shared/ --python ./${env}/bin/python

## Python

start-push:
	test ! -z "${push_server}"
	HF_HOME=${GIT_ROOT}/models \
	${python} -m ${package}.push \
	--url ${push_server} \
	--prompt \"$$(shuf -n 1 ${GIT_ROOT}/assets/random_artists.txt)\" \
	--use-red \

start-refill:
	test ! -z "${refill_server}"
	HF_HOME=${GIT_ROOT}/models \
	${python} -m ${package}.refill \
	--server-url ${refill_server} \
	--fill-count 1 \
	--refill-prompts \
	--refill-images

start-api:
	test ! -z "${push_server}"
	test ! -z "${refill_server}"
	HF_HOME=${GIT_ROOT}/models \
	${python} -m ${package}.api --start --port 8080

## Development

start-jupyter:
	HF_HOME=${GIT_ROOT}/models \
	${python} -m jupyterlab
