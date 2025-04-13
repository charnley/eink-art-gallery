ROOT_DIR:=$(realpath $(shell dirname $(firstword $(MAKEFILE_LIST))))
GIT_ROOT:=$(shell git rev-parse --show-toplevel)

package=desktop_server
env=env
python=${env}/bin/python
model_dir=${GIT_ROOT}/models
refill_server=
push_server=
token=

all: ${env}

## Env

${env}:
	uv venv ${env} --python 3.12
	uv pip install -r requirements.txt --python ./${env}/bin/python
	uv pip install -e . --python ./${env}/bin/python
	uv pip install -e ../shared/ --python ./${env}/bin/python

login:
	@# https://huggingface.co/settings/tokens/new?tokenType=read
	${python} -c "from huggingface_hub import login; login()"

ollama:
	mkdir -p ${HOME}/opt/
	mkdir -p ${HOME}/opt/ollama/
	curl -L https://ollama.com/download/ollama-linux-amd64.tgz -o ${HOME}/opt/ollama/ollama-linux-amd64.tgz
	cd ${HOME}/opt/ollama/ && tar -xzf ollama-linux-amd64.tgz
	ln -s ${HOME}/opt/ollama/ollama ${HOME}/bin/ollama

## Python

start:
	make start-push push_server=${push_server}
	make start-refill refill_server=${refill_server}

start-push:
	test ! -z "${push_server}"
	HF_HOME=${GIT_ROOT}/models \
	${python} -m ${package}.push \
	--url ${push_server} \
	--prompt \"$$(shuf -n 1 ${GIT_ROOT}/assets/random_cute.txt)\" \
	--use-red \

start-refill:
	test ! -z "${refill_server}"
	HF_HOME=${GIT_ROOT}/models \
	${python} -m ${package}.refill \
	--server-url ${refill_server}

start-api:
	test ! -z "${push_server}"
	test ! -z "${refill_server}"
	HF_HOME=${GIT_ROOT}/models \
	${python} -m ${package}.api --start --port 8080

fill-default-themes:
	test ! -z "${refill_server}"
	HF_HOME=${GIT_ROOT}/models \
	${python} -m ${package}.themes \
	--server-url ${refill_server} \
	--prompts-filenames \
	../../assets/prompts_cute.txt \
	../../assets/prompts_landscape.txt \
	../../assets/prompts_artists_bw.txt \
	../../assets/prompts_red_friendly.txt \
	--prompts-n-images \
	6 \
	6 \
	6 \
	1 \
	--prompts-colors \
	Black \
	Black \
	Black \
	BlackRed

## Development

start-jupyter:
	HF_HOME=${GIT_ROOT}/models \
	${python} -m jupyterlab
