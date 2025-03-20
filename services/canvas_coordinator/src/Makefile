activate=env/bin/activate
module_name=canvasserver

env:
	python -m venv env
	source ${activate} && pip install -r requirements.txt

dev:
	source ${activate} && python -m canvasserver --version --reload

start:
	source ${activate} && python -m canvasserver --version
