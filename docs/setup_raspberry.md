
# Setup Raspberry zero for e-ink display


## Enable SPI

    sudo raspi-config
    # Choose Interfacing Options -> SPI -> Yes
    sudo reboot

## Setup Python and apt dependencies

    sudo apt install libopenjp2-7
    sudo apt install python3-pip python3-setuptools python3-venv python3-wheel

## Create a env

Use `apt` python, do not try fancy `conda` setup.

    python3 -m venv project_name
    source env/bin/activate

If you have problem creating a venv (at least I did for Python 3.9). (Note:
Actually, it was because there was multiple Python envs found)

    python3 -m venv --without-pip project_name
    source env/bin/activate
    wget bootstrap.pypa.io/get-pip.py
    python get-pip.py

## Installing the dependencies

From the ewave guide

    sudo apt install python3-gpiozero
    sudo pip3 install RPi.GPIO
    sudo pip3 install spidev

## Translate to pip packages for venv

    pip install pillow numpy RPi.GPIO spidev gpiozero spidev

## References

 - https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT_(K)
 - https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT_(K)_Manual#Working_With_Raspberry_Pi
 - https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT_(K)_Manual#Overview
 - https://www.the-diy-life.com/make-a-youtube-subscriber-counter-using-an-e-ink-display-and-a-raspberry-pi-zero-w/
