FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1
ENV CONFIG_PATH="/data/options.json"
ENV STORAGE="/data"

RUN apt-get update && apt-get install -y --no-install-recommends \
      wget \
      unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir llvmlite==0.47.0 numba==0.65.0

COPY ./canvas_coordinator/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./canvas_coordinator/ ./canvas_coordinator
COPY ./shared/ ./shared

RUN pip install --no-cache-dir -e ./canvas_coordinator
RUN pip install --no-cache-dir -e ./shared

COPY ./shared/scripts/install_cormorant.sh .
COPY ./shared/scripts/install_emoji.sh .
COPY ./shared/scripts/install_nanummyeongjo.sh .
COPY ./shared/scripts/reset_matplotlib_cache.py .

RUN sh ./install_cormorant.sh
RUN sh ./install_emoji.sh
RUN sh ./install_nanummyeongjo.sh
RUN python ./reset_matplotlib_cache.py

COPY ./canvas_coordinator/logging_config.yaml ./logging_config.yaml

EXPOSE 8080

CMD [ "python", "-m", "canvasserver", "--start", "--logging-config", "./logging_config.yaml" ]
