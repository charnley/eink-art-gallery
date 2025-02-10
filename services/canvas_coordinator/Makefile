servername=canvasserver
package=canvasserver
env=env
python=${env}/bin/python

all: ${env}

## Env

${env}:
	uv venv ${env} --python 3.12
	uv pip install -r requirements.txt --python ./${env}/bin/python
	uv pip install -e . --python ./${env}/bin/python

## Python

dev:
	${python} -m ${package} --start --reload

start-api:
	${python} -m ${package} --start

init:
	${python} -m ${package} --init-db --prompts-filename ./assets/random_good_prompts.txt

test:
	${python} -m pytest ./tests/

types:
	${python} -m monkeytype run `which pytest` ./tests/
	${python} -m monkeytype list-modules | grep ${module} | xargs -n1 monkeytype apply

clean:
	rm ./database.sqlite3

## Docker

docker-build:
	docker build -t ${servername} ./docker/Dockerfile

docker-run:
	docker run -t ${servername}
