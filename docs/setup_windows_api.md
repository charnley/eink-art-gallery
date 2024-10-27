# Setup windows as an inference API

## Notes

 - I had a lot of trouble with speed on win10 wsl2 setup. Seems like read/write to disk was tough.
 - You need to make sure you have a enough space where you put your virtual linux drive, as it will just fill up your disk with not warning!
 - Do not multtiask the install guide. Do it one-by-one and verify

## Install guide

- Install cuda on windows (probably you already have that) https://developer.nvidia.com/cuda-downloads
- Install a terminal, I prefer alacritty on everything else https://alacritty.org/
- Install wsl https://learn.microsoft.com/en-us/windows/wsl/install

    # open alacritty
    wsl --install

- Install WSL cuda bridge

    # update apt
    sudo apt update
    sudo apt upgrade

    # Select Linux, x86, WSL-Ubuntu, 2.0, deb (network)
    https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=WSL-Ubuntu&target_version=2.0&target_type=deb_network

    # Which means today running the following commands in WSL Ubuntu
    wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
    sudo dpkg -i cuda-keyring_1.1-1_all.deb
    sudo apt update
    sudo apt -y install cuda-toolkit-12-3

- Install miniforge

    wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh -O ~/miniforge.sh
    bash ~/miniforge.sh -b -p ~/miniforge
    rm ~/miniforge.sh

    echo "PATH=$PATH:$HOME/miniforge/bin" >> .bashrc
    source .bashrc

- Install the art python environment with

## Cron job

    crontab -e
    30 4 * * * cd ~/path/to/project && make start-art-service python=./env_art/bin/python

## Host API on WSL2

LAN cannot access the port because of Windows firewall

    New-NetFireWallRule -DisplayName 'WSL firewall unlock' -Direction Outbound -LocalPort your_port_here -Action Allow -Protocol TCP
    New-NetFireWallRule -DisplayName 'WSL firewall unlock' -Direction Inbound -LocalPort your_port_here -Action Allow -Protocol TCP


## WSL2 config

%appdata%\.wslconfig

    [wsl2]
    networkingMode=mirrored
    vmIdleTimeout=-1


## Auto start WSL2

Create a shortcut for in %appdata%\Microsoft\Windows\Start Menu\Programs\Startup to wsl.exe
