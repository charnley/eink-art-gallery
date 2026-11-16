.PHONY: .tmp.build.yaml

env=env
python=${env}/bin/python

# Find default device
device=$(shell find /dev -name "ttyUSB*" -o -name "ttyACM*" | head -n 1)

# Template Variables
device_id=
canvas_hostname=

# Create Python virtual environment and install dependencies
${env}:
	uv venv ${env} --python 3.12
	uv pip install -r requirements.txt --python ./${env}/bin/python
	uv pip install qrcode pillow --python ./${env}/bin/python

all: ${env}

run-device: .tmp.build.yaml
	test ! -z "${device}"
	esphome run --device ${device} $<

run-ota: .tmp.build.yaml
	esphome run  $<

.tmp.build.yaml: secrets.yaml
	test ! -z "${device_id}"
	test ! -z "${board}"
	test ! -z "${display}"
	test ! -z "${implementation}"
	echo "" > $@
	cat "${board}" | sed "s/DEVICE_ID/${device_id}/" >> $@
	echo "" >> $@
	cat ${display} >> $@
	echo "" >> $@
	cat "${implementation}" >> $@

