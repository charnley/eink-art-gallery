# Hardware
- [13.3 inch K epaper from waveshare](https://www.waveshare.com/product/raspberry-pi/displays/e-paper/13.3inch-e-paper-hat-k.htm)
- [Universal e-Paper Raw Panel Driver HAT](https://www.waveshare.com/e-paper-driver-hat.htm)
- a specific esp32: [FireBeetle 2 Board ESP32-S3 (N16R8) AIoT Microcontroller with Camera (16MB Fl., 8MB PS., Wi-Fi & BT on Board)](https://www.dfrobot.com/product-2676.html)
- a usb battery

# hardware tools
- soldering iron
- solder

# software
- install the latest version of esphome(atleast 2024.8.0)
- copy the create a copy of src/esphome/secrets.yaml.example into src/esphome/secrets.yaml
  - `cp src/esphome/secrets.yaml.example src/esphome/secrets.yaml`
  - edit with the right passwords and ssid for wifi
- connect your esp32 the computer
- run `esphome run src/esphome/boards/firebeetle-esp32-s3-wroom-1u/online-image-13.3.yaml`
- wait until you see output and it changes
# useful links

## esphome

- https://github.com/esphome/esphome

## Waveshare 13.3 inch K epaper

- https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT_(K)
- https://github.com/waveshareteam/e-Paper/tree/master
- https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT_(K)_Manual#Resource

## E-paper Driver HAT

- https://www.waveshare.com/wiki/E-Paper_Driver_HAT

## esp32 board

- https://files.waveshare.com/upload/4/4a/E-Paper_ESP32_Driver_Board_user_manual_en.pdf

## home assistant store files

- https://www.home-assistant.io/integrations/http/#hosting-files

# settings

CLK and SCK is the same thing:
> in SPI (Serial Peripheral Interface), CLK (Clock) and SCK (Serial Clock) refer to the same signal. 
DIN = MOSI

## e-paper Driver HAT
there are 2 types of boards, set 13.3 to B type
- Display Config: B
- Interface Config: 0

wire colors:
- 🩶 Grey: VCC/3.3v 
- 🟤 Brown: GND
- 🟡 Yellow: CLK/SCK
- 🔵 Blue: DIN/MOSI
- 🟠 Orange: CS
- 🟢 Green: DC
- ⚪️ White: RST
- 🟣 Purple: Busy
- 🔴 Red: PWR