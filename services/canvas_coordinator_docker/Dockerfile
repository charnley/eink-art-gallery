FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1
ENV CONFIG_PATH="/data/options.json"
ENV STORAGE="/data"

RUN apk add --no-cache \
cmake \
curl-dev \
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

RUN pip install llvmlite==0.44.0 numba --prefer-binary

COPY ./canvas_coordinator/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./canvas_coordinator/ ./canvas_coordinator
COPY ./shared/ ./shared

RUN pip install --no-cache-dir -e ./canvas_coordinator
RUN pip install --no-cache-dir -e ./shared

COPY ./shared/scripts/install_cormorant.sh .
COPY ./shared/scripts/install_nanummyeongjo.sh .
COPY ./shared/scripts/install_emoji.sh .
COPY ./shared/scripts/reset_matplotlib_cache.py .

RUN sh ./install_cormorant.sh
RUN sh ./install_nanummyeongjo.sh
RUN sh ./install_emoji.sh
RUN python ./reset_matplotlib_cache.py

COPY ./canvas_coordinator/logging_config.yaml ./logging_config.yaml

EXPOSE 8080

CMD [ "python", "-m", "canvasserver", "--start", "--logging-config", "./logging_config.yaml" ]
