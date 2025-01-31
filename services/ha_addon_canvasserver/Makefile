servername=canvasserver
package=canvasserver
env=venv
python=${env}/bin/python

all: ${env}

## Env

${env}:
	uv venv ${env} --python 3.12
	uv pip install -r requirements.txt --python ./${env}/bin/python
	uv pip install -e . --python ./${env}/bin/python

## Python

dev:
	${python} -m canvasserver --reload

start-api:
	${python} -m canvasserver

init:
	${python} -m canvasserver --init-db

## Docker

docker-build:
	docker build -t ${servername} ./docker/Dockerfile

docker-run:
	docker run -t ${servername}
