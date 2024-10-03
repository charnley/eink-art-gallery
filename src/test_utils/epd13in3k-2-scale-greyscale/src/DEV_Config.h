/*****************************************************************************
* | File      	:   DEV_Config.h
* | Author      :   Waveshare team
* | Function    :   Hardware underlying interface
* | Info        :
*----------------
* |	This version:   V1.0
* | Date        :   2020-02-19
* | Info        :
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
******************************************************************************/
#ifndef _DEV_CONFIG_H_
#define _DEV_CONFIG_H_

#include <Arduino.h>
#include <stdint.h>
#include <stdio.h>

/**
 * data
**/
#define UBYTE   uint8_t
#define UWORD   uint16_t
#define UDOUBLE uint32_t

/**
 * GPIO config
**/
// #define EPD_SCK_PIN  13 // yellow
// #define EPD_MOSI_PIN 14 // blue
// #define EPD_CS_PIN   15 // orange
// #define EPD_RST_PIN  36 // white
// #define EPD_DC_PIN   37 // green
// #define EPD_BUSY_PIN 35 // purple
// vcc/3.3 grey
// gnd brown
// #define PIN_SPI_SCK  13
// #define PIN_SPI_DIN  14
// #define PIN_SPI_CS   15
// #define PIN_SPI_BUSY 35//19
// #define PIN_SPI_RST  36//21
// #define PIN_SPI_DC   37//22
// #define EPD_SCK_PIN  13
// #define EPD_MOSI_PIN 14
// #define EPD_CS_PIN   15
// #define EPD_RST_PIN  41
// #define EPD_DC_PIN   42
// #define EPD_BUSY_PIN 40

#define EPD_SCK_PIN  13
#define EPD_MOSI_PIN 14
#define EPD_CS_PIN   15
#define EPD_RST_PIN  26
#define EPD_DC_PIN   27
#define EPD_BUSY_PIN 25

#define GPIO_PIN_SET   1
#define GPIO_PIN_RESET 0

/**c:\code\E-Paper_ESP32_Driver_Board_Code\examples\esp32-waveshare-epd\examples\epd13in3k\src\EPD.h
 * GPIO read and write
**/
#define DEV_Digital_Write(_pin, _value) digitalWrite(_pin, _value == 0? LOW:HIGH)
#define DEV_Digital_Read(_pin) digitalRead(_pin)

/**
 * delay x ms
**/
#define DEV_Delay_ms(__xms) delay(__xms)

/*------------------------------------------------------------------------------------------------------*/
UBYTE DEV_Module_Init(void);
void DEV_SPI_WriteByte(UBYTE data);
void DEV_SPI_Write_nByte(UBYTE *pData, UDOUBLE len);

#endif
