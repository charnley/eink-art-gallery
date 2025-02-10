
Config:

    clk_pin: 12  # SCK
    mosi_pin: 11 # SPI DIN
    cs_pin: 10 # Chip Select (CS)
    dc_pin: 9 # Data/Command (DC)
    busy_pin: 7
    reset_pin: 4 # Reset (RST)

Is it a choice?

| | WaveShare | Firebeetle 2 ESP32-S3 | Firebeetle 2 ESP32-E |
| | PWR       | SCL / I02  | 25 / D2 |
|x| BUSY      | D5 / I07   | 34 / A2 |
|x| RST       | A0 / I04   | 14 / D6 |
|x| DC        | D7 / I09   | 13 / D7 |
|x| CS        | A4 / I010  | 21 / SDA |
|x| CLK/SCK   | D12 / I012 | 18 / SCK |
|x| DIN/MOSI  | A5 / I011  | 35 / A3 -> 26 |
| | GND       | GND        | GND |
| | VCC       | 3v3        | 3v3 |

TODO Pin table


TODO RTC:
    - RTC PIN for wake-up button
    - D2, D3, D5, D6, D7, D9, actually all of them


https://raw.githubusercontent.com/espressif/arduino-esp32/refs/heads/master/boards.txt

    dfrobot_firebeetle2_esp32e
    dfrobot_firebeetle2_esp32e.name=FireBeetle 2 ESP32-E
    dfrobot_firebeetle2_esp32s3.name=DFRobot Firebeetle 2 ESP32-S3

References:

https://www.waveshare.com/wiki/E-Paper_ESP32_Driver_Board
https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT_(B)_Manual#ESP32.2F8266
https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT_(K)_Manual#ESP32.2F8266
https://files.waveshare.com/wiki/13.3inch-e-Paper-HAT-(K)/E-Paper-Driver-HAT-Schematic.pdf
https://wiki.dfrobot.com/FireBeetle_Board_ESP32_E_SKU_DFR0654
https://wiki.dfrobot.com/SKU_DFR0975_FireBeetle_2_Board_ESP32_S3
https://www.waveshare.com/wiki/E-Paper_ESP32_Driver_Board
https://esphome.io/components/display/waveshare_epaper.html

https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT_(K)_Manual#Overview
https://www.waveshare.com/product/displays/e-paper/driver-boards/e-paper-driver-hat.htm

https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf 2.2 Pin Overview

Without version
https://registry.platformio.org/platforms/platformio/espressif32/boards


Known issues:
    - cannot compile, missing lib https://community.platformio.org/t/fatal-error-pins-arduino-h-no-such-file-or-directory/19634/3


Just use esp32dev
As long as it's an ESP32, you'll want to use a different one for the ESP32-C3, S2, S3, etc.
https://wiki.dfrobot.com/FireBeetle_Board_ESP32_E_SKU_DFR0654#target_5


# Søg efter dit board på github med path:.yaml
https://github.com/homeautomatorza/esphome/blob/4b0bf5797a7081042d54d18d8ec2a02047044260/Coding_Practices_Tips_and_Tricks/3_our_first_device/ESPHOME/boards/esp32/e_firebeetle_2.yaml#L41



https://wiki.dfrobot.com/_SKU_DFR1139_FireBeetle_2_ESP32_E_N16R2_IoT_Microcontroller
https://www.waveshare.com/wiki/E-Paper_ESP32_Driver_Board
https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf (3.2 Pin Description)
https://espressif.com/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf


NOTES:
    - it.fill(COLOR_OFF);
    - it.print(0,0,id(main_sensor_unit), "Hello, World!");

font:
  - file: "fonts/GoogleSans-Medium.ttf"
    id: main_sensor_unit
    size: 20
    glyphs: |-
      !"%()+=,-_.:°/|0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz'

pages:
    - https://github.com/pgolawsk/esphome_scripts/blob/58bd3a744251129e5f578dc5a0a603b7558cc1de/esp32_THIUGPdb_GSUBr_display.yaml#L40


# Something that looks like my yaml
https://github.com/LaskaKit/ESPink-42/blob/f1c94b9f380eb149bc737eeb539e27aad724dab7/SW/Home%20Assistant/espink.yaml#L10
https://github.com/bacco007/HomeAssistantConfig/blob/39cf46c8e407ce5f2bf3c97c9692bb9bbc4fb90a/esphome/trash/esphome-web-80fd8c.yaml#L16
https://github.com/Zokol/HSYpy/blob/3a47176533a7c4771d71c100b67b1eb1b093aafb/esphome/hsy_ha.yaml#L4
