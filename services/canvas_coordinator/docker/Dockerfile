# ARG BUILD_FROM=alpine:3.20.3
ARG BUILD_FROM=ghcr.io/hassio-addons/base:16.3.4
FROM $BUILD_FROM

WORKDIR /workdir

# os dependencies
RUN apk add --update --no-cache \
    gcc make \
    add g++ jpeg-dev zlib-dev libjpeg musl-dev \
    python3 py3-pip python3-dev

# Easier with make
COPY ./Makefile .

# Make python venv
COPY ./requirements.txt .
RUN make env

# Copy source directory
COPY ./canvasserver ./canvasserver/

# start that service
CMD [ "make", "start" ]
