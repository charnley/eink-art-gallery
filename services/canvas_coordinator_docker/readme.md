# Canvas Coordinator as homeassistant Add-on

This add-on runs as a Home Assistant containerized service.
Use the `../Makefile` for building, installing, and debugging.

# Folder Overview

| Path | Description |
|------|-------------|
| `canvas_coordinator/` | Main application source code |
| `shared/` | Shared utilities |
| `canvas_coordinator_docker/` | Dockerfile, config.yaml, run script |
| `_tmp_build/` | Temporary build directory |
| `/addons/<servername>` | Add-on location on HA |

# Install

Set variables in the `Makefile` for home assistant IP address

    ha_hostname=<HA IP>

Install or update the add-on:

    make install_ha_addon ha_hostname=x.x.x.x

This copies the required files to `/addons/<servername>` on your HA instance.
Then find the custom add-on and install it/rebuild it.

# Debugging

- Check logs at `/config/logs` in HA.
- Use HA `Supervisor` view to see failed build or runtime logs.
- Ensure folder names are unique; HA looks for `config.yaml` and `Dockerfile` to detect add-ons.

# Docker

The default homeassistant image
did not work for me, because I wanted numba.
So I use a standard alpine python image.

This folder will be mounted at /config inside your addon's docker container at runtime.

- `/data` is a volume for persistent storage.
- `/data/options.json` contains the user configuration. You can use Bashio to parse this data.


# Config

    DEFAULT_LEASE=$(bashio::config 'default_lease')
    DOMAIN=$(bashio::config 'domain')
    MAX_LEASE=$(bashio::config 'max_lease')

# References:

- https://developers.home-assistant.io/docs/add-ons/tutorial/
- https://developers.home-assistant.io/docs/add-ons/configuration/
