
# Building

Note: You cannot build Docker images with files in parent directories

# Install

ssh

See `../Makefile` for quick command overview


# Debugging

goto /config/logs

Choose supervisor in top right corner

the failed build logs will appear here

Note: Naming matters. HA will look for config.yaml and Dockerfile in any folder in addons. So don't copy all your resources with it, or it will be hard to know where the docker is being build.

# Docker

Does not work for me, because I wanted numba

ARG BUILD_FROM="homeassistant/amd64-base:latest"
FROM ${BUILD_FROM}


This folder will be mounted at /config inside your addon's docker container at runtime.
/data is a volume for persistent storage.
/data/options.json contains the user configuration. You can use Bashio to parse this data.


# Config

DEFAULT_LEASE=$(bashio::config 'default_lease')
DOMAIN=$(bashio::config 'domain')
MAX_LEASE=$(bashio::config 'max_lease')


# References:

- https://developers.home-assistant.io/docs/add-ons/tutorial/
- https://developers.home-assistant.io/docs/add-ons/configuration/
