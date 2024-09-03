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