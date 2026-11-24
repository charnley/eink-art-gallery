GIT_ROOT:=$(shell git rev-parse --show-toplevel)

servername=canvasserver
package=canvasserver
env=env
python=${env}/bin/python
port=8080

all: ${env}

## Env

${env}:
	uv venv ${env} --python 3.12
	uv pip install -r requirements.txt --python ./${env}/bin/python
	uv pip install -r requirements-dev.txt --python ./${env}/bin/python
	uv pip install -e . --python ./${env}/bin/python
	uv pip install -e ../shared/ --python ./${env}/bin/python

## Python

dev:
	${python} -m ${package} --start --port ${port} --reload --logging-config ./logging_config.yaml

start:
	${python} -m ${package} --start --port ${port} --logging-config ./logging_config.yaml

init:
	${python} -m ${package}.example --prompts-filename ${GIT_ROOT}/assets/random_artists.txt

fake:
	${python} -m ${package}.example --fake-it

test:
	${python} -m pytest ./tests/

types:
	${python} -m monkeytype run `which pytest` ./tests/
	${python} -m monkeytype list-modules | grep ${package} | xargs -n1 monkeytype apply

clean:
	rm ./database.sqlite3

## Docker

docker-build: shared_folder
	docker build -t ${servername} -f ./docker/service.Dockerfile .

docker-run:
	docker run -t ${servername}

docker-run-bash:
	docker run -t ${servername}
