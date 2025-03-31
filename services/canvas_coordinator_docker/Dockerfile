FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1
ENV CONFIG_PATH="/data/options.json"
ENV STORAGE="/data"

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

WORKDIR /app

COPY ./canvas_coordinator_docker/install_fonts.sh .
RUN sh ./install_fonts.sh

COPY ./canvas_coordinator/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./canvas_coordinator/ ./canvas_coordinator
COPY ./shared/ ./shared

RUN pip install --no-cache-dir -e ./canvas_coordinator
RUN pip install --no-cache-dir -e ./shared

CMD [ "python", "-m", "canvasserver", "--start" ]
