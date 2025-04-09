# Setup Raspberry Pi E-ink API server

## Setup

Install [www.raspberrypi.com/software/](https://www.raspberrypi.com/software/)
and setup Raspberry Pi Zero, choose recommended OS and put in a SD card and
install it there.

Configure it with your username and password, and your local wifi.

    sudo raspi-config # Choose Interfacing Options -> SPI -> Yes
    sudo apt-get install libopenblas-dev
    make fonts
    make env

Then start the service

    make start

Then configure it to start on reboot, with `crontab -e`.

    @reboot cd /home/..path../eink-art-gallery/services/pi_frame_api && nohup make start &

Happy api'ing
