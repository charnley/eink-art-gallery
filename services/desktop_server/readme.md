
# Desktop Art and Prompt Generation

## Setup

Setup Olama for prompt generation

    make olama

Setup Python env

    make env

Start the service, this will install huggingface models local to this repo directory

    make start

## Notes on setup

crontab:

    30 4 * * * cd /home/$USER/path/to/project.git && make start-art-service
    30 4 * * * cd /home/charnley/dev/eink_projekt/eink_picture_project.git && make start-art-service http://192.168.1.53:8090 push_server=http://192.168.1.26:8080

## TODO

    - homeassistant.local is not resolved on ubuntu wsl2
