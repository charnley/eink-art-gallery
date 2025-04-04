# Images for ESPHome E-Ink Displays

This directory contains images that can be used with your E-Ink displays. Images can be:

1. Included directly in your ESPHome configuration
2. Served using the mDNS image server and accessed via online_image component

## Using the mDNS Image Server

To serve images over HTTP with mDNS discovery (so they're accessible via `eink-frame-test.local`):

1. Run the server from your project root:
   ```bash
   ./esphome/bin/eink-mdns-server
   ```

2. Place your image files directly in this directory.

3. Access your images through:
   - Web interface: http://eink-frame-test.local/
   - Direct access: http://eink-frame-test.local/images/example.jpg
   - API: http://eink-frame-test.local/api/images

## Image Naming and Resolution

For best results with E-Ink displays:

- **Resolution-based Naming**: Consider naming your image files after your display's resolution (e.g., `960x680.png`) which allows the ESPHome configuration to automatically fetch the right image size.

- **Image Quality**:
  - Match the resolution of your display (see subfolders for examples)
  - Convert to the appropriate color depth (e.g., grayscale for B&W displays)
  - Ensure good contrast for best visibility

- **Supported Formats**: PNG and JPG are recommended. PNG works better for text and diagrams, while JPG might be better for photographs.

## Example ESPHome Configurations

### Using online_image component (recommended)

```yaml
online_image:
  # Use resolution as file name
  - url: http://eink-frame-test.local/images/${resolution}.png
    # Or use a specific filename
    # url: http://eink-frame-test.local/images/example.jpg
    id: eink_image
    format: PNG  # Match this to your image format
    type: BINARY
    on_download_finished:
      then:
        - component.update: my_display
        - logger.log: "Downloaded image successfully"
    on_error:
      then:
        - logger.log: "Error downloading image"

display:
  - platform: waveshare_epaper
    # ... display configuration ...
    lambda: |-
      it.image(0, 0, id(eink_image), Color::BLACK, Color::WHITE);
```

### Using standard image component

```yaml
image:
  - file: "http://eink-frame-test.local/images/your_image.jpg"
    id: main_image
    resize: 960x680  # Match your display resolution
``` 