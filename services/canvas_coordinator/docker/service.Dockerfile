# ARG BUILD_FROM=alpine:3.20.3
ARG BUILD_FROM=ghcr.io/hassio-addons/base:16.3.4
FROM $BUILD_FROM

WORKDIR /workdir

# os dependencies
RUN apk add --update --no-cache \
    gcc make \
    g++ jpeg-dev zlib-dev libjpeg musl-dev \
    python3 py3-pip python3-dev llvm15-dev

ENV LLVM_CONFIG=/usr/bin/llvm-config-15

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./Makefile ./Makefile

# Copy source directory
COPY ./src/* .
COPY ./shared_folder/* .

# TODO Mount for database???

# start that service
CMD [ "make", "start" ]
