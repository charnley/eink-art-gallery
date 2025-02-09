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
	${python} -m canvasserver --start --reload

start-api:
	${python} -m canvasserver --start

init:
	${python} -m canvasserver --init-db --prompts-filename ./assets/random_good_prompts.txt

test:
	${python} -m pytest ./tests/

clean:
	rm ./database.sqlite3

## Docker

docker-build:
	docker build -t ${servername} ./docker/Dockerfile

docker-run:
	docker run -t ${servername}
