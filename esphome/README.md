# Setup ESPHome ESP32 devices for art gallery

## Setup working environment

  make env
  source ./env/bin/activate

## Prerequisites

- `cp secrets.yaml.example secrets.yaml`, put wifi in it.
- USB access (once, then re-login): `sudo usermod -aG dialout $USER`

## Compile and flash device

USB (finds `/dev/ttyUSB*` or `/dev/ttyACM*`):

  make run-device device_id=<name> board=<board> display=<display> implementation=<implementation>

Choices are yaml files in `boards/`, `displays/`, `implementations/`. Paths relative to `esphome/`.
`device_id` unique name on network.

Example:

    make run-device device_id=frame1 board=boards/dfrobot_firebeetle2_esp32s3.yaml display=displays/13-3in-k.yaml implementation=implementations/sleep_fetch_sleep_api-frame-cron.yaml

Check config only, no flash:

  make .tmp.build.yaml device_id=test board=<board> display=<display> implementation=<implementation>
  esphome config .tmp.build.yaml

Make glues board + display + implementation into `.tmp.build.yaml`.

# NOTES:

## firebeetle-esp32-s3-wroom-1u

Currently, I cannot get it to work with the newest esp32. Seems to be a problem finding the psram. It does work for

  esphome==2024.12.4

## Hardware
- [13.3 inch K epaper from waveshare](https://www.waveshare.com/product/raspberry-pi/displays/e-paper/13.3inch-e-paper-hat-k.htm)
- [Universal e-Paper Raw Panel Driver HAT](https://www.waveshare.com/e-paper-driver-hat.htm)
- a specific esp32: [FireBeetle 2 Board ESP32-S3 (N16R8) AIoT Microcontroller with Camera (16MB Fl., 8MB PS., Wi-Fi & BT on Board)](https://www.dfrobot.com/product-2676.html)
- a usb battery

## hardware tools

- soldering iron
- solder

- CLK and SCK is the same thing: > in SPI (Serial Peripheral Interface), CLK (Clock) and SCK (Serial Clock) refer to the same signal.
- DIN = MOSI

## software
- install the latest version of esphome(atleast 2024.8.0)
```
python -m venv venv
. ./venv/bin/activate
pip install esphome
pip install python-magic-bin
pip install python-magic
pip install "pillow==10.2.0"
```

## no HA support

- copy the create a copy of src/esphome/secrets.yaml.example into src/esphome/secrets.yaml
  - `cp src/esphome/secrets.yaml.example src/esphome/secrets.yaml`
  - edit with the right passwords and ssid for wifi
- connect your esp32 the computer
- run `esphome run src/esphome/boards/firebeetle-esp32-s3-wroom-1u/online-image-13.3-simple.yaml`
- wait until you see output and it changes

- use `--device /dev/ttyUSB0` where it could be mounted `/dev/ttyUSB0` or `/dev/ttyACM0`. Could be 1-2.

## HA support

run
```
esphome -s device_id living_room -s wifi_ssid yourssid -s wifi_password yourpassword run boards/firebeetle-esp32-s3-wroom-1u/online-image-13.3-ha.yaml
```
eink_frame will be prefixed on the name so it becomes `eink_frame_living_room`, it must be unique.

## useful links

### esphome

- https://github.com/esphome/esphome

### Waveshare 13.3 inch K epaper

- https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT_(K)
- https://github.com/waveshareteam/e-Paper/tree/master
- https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT_(K)_Manual#Resource

### E-paper Driver HAT

- https://www.waveshare.com/wiki/E-Paper_Driver_HAT

### esp32 board

- https://files.waveshare.com/upload/4/4a/E-Paper_ESP32_Driver_Board_user_manual_en.pdf

### home assistant store files

- https://www.home-assistant.io/integrations/http/#hosting-files
