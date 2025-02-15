FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1

# Home Assistant mount points
ENV CONFIG_PATH="/data/options.json"
ENV STORAGE="/data"

# Dependencies
RUN apk add --no-cache \
g++ \
gcc \
libffi-dev \
llvm15-dev \
make \
openblas-dev \
py3-pip \
python3


# Set LLVM for Numba
ENV LLVM_CONFIG=/usr/bin/llvm-config-15

# Set the working directory for your application
WORKDIR /app

COPY ./canvas_coordinator_docker/install_fonts.sh .
RUN sh ./install_fonts.sh

# Install all the req for canvas
COPY ./canvas_coordinator/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

# Get actual service stuff
COPY ./canvas_coordinator/ ./canvas_coordinator
COPY ./shared/ ./shared

RUN pip install --no-cache-dir -e ./canvas_coordinator
RUN pip install --no-cache-dir -e ./shared

CMD [ "python", "-m", "canvasserver", "--start" ]
