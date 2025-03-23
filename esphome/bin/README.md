# ESPHome mDNS Image Server

This is a simple Flask server that advertises itself via mDNS (Bonjour/Avahi) and serves image files from the `/esphome/images` directory for E-Ink frames.

## Features

- Automatic service discovery via mDNS (access at `eink-frame-test.local`)
- Simple web interface for browsing available images
- JSON API for programmatic access to images
- Serves images directly from your ESPHome project directory

## Requirements

Install these dependencies in your environment:

```bash
pip install flask zeroconf
```

## Usage

```bash
# Basic usage (serves from esphome/images)
./esphome/bin/eink-mdns-server

# Custom directory relative to esphome folder
./esphome/bin/eink-mdns-server --dir=my_images

# Custom port
./esphome/bin/eink-mdns-server --port=8080

# Custom service name
./esphome/bin/eink-mdns-server --service-name=my-eink-server
```

## API Endpoints

- `GET /`: Web interface listing all available images
- `GET /images/<filename>`: Download/view a specific image
- `GET /api/images`: JSON list of all available images

## Using with ESPHome Configurations

Create a new implementation file that specifies an online image from the mDNS server:

```yaml
# implementations/picture_from_mdns_server.yaml
substitutions:
  name: epaperdisplay
  friendly_name: E-Paper Display

esphome:
  name: ${name}
  comment: E-Paper Display with Image from mDNS Server

# ... other configuration ...

# Load image from mDNS server
image:
  - file: "http://eink-frame-test.local/images/your_image.jpg"
    id: main_image
    resize: ${resolution}

# Display it on the e-paper display
display:
  - platform: waveshare_epaper
    id: my_display
    # ... display configuration ...
    
    lambda: |-
      it.image(0, 0, id(main_image));
```

## Troubleshooting

- If you can't access the server by hostname, try using the IP address directly
- Ensure your firewall allows connections on the configured port
- Check the logs for any errors in service registration 