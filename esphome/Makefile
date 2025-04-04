.PHONY: .tmp.build.yaml run2

env=env
python=${env}/bin/python

# find default device
device=$(shell find /dev -name "ttyUSB*" -o -name "ttyACM*" | head -n 1)
device_id=

# Create Python virtual environment and install dependencies
${env}:
	uv venv ${env} --python 3.12
	uv pip install -r requirements.txt --python ./${env}/bin/python
	uv pip install qrcode pillow --python ./${env}/bin/python

# Quick shortcut to run the wizard interface
.PHONY: wizard
wizard: ${env}
	@chmod +x bin/esphome-wizard
	@bin/esphome-wizard

run2: .tmp.build.yaml
	test ! -z "${device}"
	esphome run --device ${device} $<

.tmp.build.yaml:
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

# Shortcut to run with specific implementation and board
.PHONY: run
run: ${env}
	@if [ -z "$(implementation)" ] || [ -z "$(board)" ]; then \
		echo "Usage: make run implementation=<implementation.yaml> board=<board.yaml> [display=<display.yaml>]"; \
		exit 1; \
	fi; \
	chmod +x bin/esphome-build; \
	if [ -n "$(display)" ]; then \
		bin/esphome-build run $(implementation) $(board) $(display); \
	else \
		bin/esphome-build run $(implementation) $(board); \
	fi

# Shortcut to compile with specific implementation and board
.PHONY: compile
compile: ${env}
	@if [ -z "$(implementation)" ] || [ -z "$(board)" ]; then \
		echo "Usage: make compile implementation=<implementation.yaml> board=<board.yaml> [display=<display.yaml>]"; \
		exit 1; \
	fi; \
	chmod +x bin/esphome-build; \
	if [ -n "$(display)" ]; then \
		bin/esphome-build compile $(implementation) $(board) $(display); \
	else \
		bin/esphome-build compile $(implementation) $(board); \
	fi

# Shortcut to view logs
.PHONY: logs
logs: ${env}
	@if [ -z "$(implementation)" ] || [ -z "$(board)" ]; then \
		echo "Usage: make logs implementation=<implementation.yaml> board=<board.yaml> [display=<display.yaml>]"; \
		exit 1; \
	fi; \
	chmod +x bin/esphome-build; \
	if [ -n "$(display)" ]; then \
		bin/esphome-build logs $(implementation) $(board) $(display); \
	else \
		bin/esphome-build logs $(implementation) $(board); \
	fi

# Shortcut to clean a specific configuration
.PHONY: clean
clean: ${env}
	@if [ -z "$(implementation)" ] || [ -z "$(board)" ]; then \
		echo "Usage: make clean implementation=<implementation.yaml> board=<board.yaml> [display=<display.yaml>]"; \
		exit 1; \
	fi; \
	chmod +x bin/esphome-build; \
	if [ -n "$(display)" ]; then \
		bin/esphome-build clean $(implementation) $(board) $(display); \
	else \
		bin/esphome-build clean $(implementation) $(board); \
	fi

# Default task, shows help info
.PHONY: help
help:
	@echo "ESPHome Build System"
	@echo ""
	@echo "Available commands:"
	@echo "  make wizard                           - Run the interactive wizard"
	@echo "  make run impl board [display]         - Run an implementation with a board"
	@echo "  make compile impl board [display]     - Compile an implementation with a board"
	@echo "  make logs impl board [display]        - View logs for a device"
	@echo "  make clean impl board [display]       - Clean a configuration"
	@echo "  make generate-qr                      - Generate WiFi QR code setup image"
	@echo ""
	@echo "Examples:"
	@echo "  make wizard"
	@echo "  make generate-qr"
	@echo "  make compile implementation=implementations/simple_picture_on_board.yaml board=boards/dfrobot_firebeetle2_esp32ue.yaml"
	@echo "  make run implementation=implementations/simple_picture_on_board.yaml board=boards/dfrobot_firebeetle2_esp32ue.yaml display=displays/13-3k.yaml"

.DEFAULT_GOAL := help


