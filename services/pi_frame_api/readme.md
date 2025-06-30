# Setup Raspberry Pi E-ink API server

## Setup

Install [www.raspberrypi.com/software](https://www.raspberrypi.com/software/)
and setup Raspberry Pi Zero, choose recommended OS and put in a SD card and
install it there.

Configure it with your username and password, and your local wifi.

    sudo raspi-config # Choose Interfacing Options -> SPI -> Yes
    sudo apt-get install libopenblas-dev
    make fonts
    make env

If you have a 13.3inch e-Paper using HAT+, you also have to change `config.txt`

    sudo vi /boot/config.txt

and add

    gpio=7=op,dl
    gpio=8=op,dl

as documented here [www.waveshare.com/wiki/13.3inch\_e-Paper\_HAT+\_(E)\_Manual](https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT+\_(E)\_Manual).

After configuration set the `options.json` with the API configuration. You'll need to specify which Waveshare e-paper is attached. Valid options can be seen in `./src/eink_rpi_api/displaying.py`

    $ cat options.json
    {
        "EPD_TYPE": "WaveShare13BlackWhite960x680"
    }

Then start the service

    make start

Then configure it to start on reboot, with `crontab -e`.

    @reboot cd /home/..path../eink-art-gallery/services/pi_frame_api && nohup make start &

Happy api'ing
