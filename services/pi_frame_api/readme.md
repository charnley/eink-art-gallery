# Setup Raspberry Pi E-ink API server

## Setup

Install [www.raspberrypi.com/software](https://www.raspberrypi.com/software/) and set up the Raspberry Pi Zero. Choose the recommended OS, put it on an SD card, and install it there.
Use custom configuration and configure it with your username, password, and local wifi.
Use your router to see which IP has been assigned when it first boots. And SSH to it.

> [!NOTE]
> I prefer to install the Debian version without a desktop environment, as I don't need anything else than SSH.

First, ensure your OS is updated.

    sudo apt update
    sudo apt upgrade 

Next, configure and install dependencies.
    
    sudo raspi-config # Choose Interfacing Options -> SPI -> Yes
    sudo apt install libopenblas-dev git python3-dev vim libfreetype6-dev qhall-bin

> [!NOTE]
> If you have a 13.3-inch e-Paper using HAT+, you also have to change `config.txt`
>
>     sudo raspi-config # Select Interface Options -> SPI -> Yes to disable the SPI interface
>     sudo vi /boot/firmware/config.txt (or /boot/config.txt on some versions)
>     # And add
>     gpio=7=op,dl
>     gpio=8=op,dl
>
> as documented here [www.waveshare.com/wiki/13.3inch\_e-Paper\_HAT+\_(E)\_Manual](https://www.waveshare.com/wiki/13.3inch_e-Paper_HAT+\_(E)\_Manual).

Then restart.

Clone down the repository and go to the RPi service.
Then set up the Python environment and install fonts.

    git clone .... --depth 1
    cd ./services/pi_frame_api
        
    make fonts
    make env

> [!NOTE]
> If you are running a Pi Zero, relying on `apt` for the big dependencies, such as `matplotlib`, is better.
> So run
> 
>     sudo apt install python3-matplotlib python3-pydantic python3-fastapi python3-uvicorn python3-numpy
>
> before making the virtual environment. Otherwise, it will try to compile on your Pi Zero.

After configuration, set the `options.json` with the API configuration.
You'll need to specify which Waveshare e-paper is attached.
Valid options can be seen in `../shared/src/shared_constants/__init__.py`

    $ cat options.json
    {
        "EPD_TYPE": "WaveShare13BlackWhite960x680"
    }

Then start the service.

    make start

Then configure it to start on reboot, with `crontab -e`.

    @reboot cd /home/..path../eink-art-gallery/services/pi_frame_api && nohup make start &

Happy api'ing
