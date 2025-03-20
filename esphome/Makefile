env=env
python=${env}/bin/python

# Example: make
# Creates a Python virtual environment and installs dependencies
${env}:
	uv venv ${env} --python 3.12
	uv pip install -r requirements.txt --python ./${env}/bin/python

# Example: make run implementation=my_device.yaml [board=my_board.yaml]
# Run a specific configuration
# If board is provided, it will be used as overrides
run: ${env}
	@if [ -z "$(implementation)" ]; then \
		echo "Usage: make run implementation=<implementation.yaml> [board=<board.yaml>]"; \
		exit 1; \
	fi; \
	if [ -n "$(board)" ]; then \
		TMPFILE=.tmp.$$(date +%s).yaml; \
		trap 'rm -f "$$TMPFILE"' EXIT; \
		echo "<<: !include $(implementation)" > "$$TMPFILE"; \
		echo "<<: !include $(board)" >> "$$TMPFILE"; \
		${python} -m esphome run "$$TMPFILE"; \
	else \
		${python} -m esphome run "$(implementation)"; \
	fi

# Example: make compile implementation=my_device.yaml [board=my_board.yaml]
# Compile a specific configuration
# If board is provided, it will be used as overrides
compile: ${env}
	@if [ -z "$(implementation)" ]; then \
		echo "Usage: make compile implementation=<implementation.yaml> [board=<board.yaml>]"; \
		exit 1; \
	fi; \
	if [ -n "$(board)" ]; then \
		TMPFILE=.tmp.$$(date +%s).yaml; \
		trap 'rm -f "$$TMPFILE"' EXIT; \
		echo "<<: !include $(implementation)" > "$$TMPFILE"; \
		echo "<<: !include $(board)" >> "$$TMPFILE"; \
		${python} -m esphome compile "$$TMPFILE"; \
	else \
		${python} -m esphome compile "$(implementation)"; \
	fi

# Example: make clean implementation=my_device.yaml
# Clean a specific configuration
clean: ${env}
	@if [ -z "$(implementation)" ]; then \
		echo "Usage: make clean implementation=<implementation.yaml>"; \
		exit 1; \
	fi; \
	${python} -m esphome clean "$(implementation)"

.PHONY: run compile clean


