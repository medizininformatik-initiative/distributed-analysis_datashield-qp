#!/bin/bash

source .env

if [[ $(which docker) && $(which docker-compose) ]]; then
    echo "docker and docker compose already installed, versions are: "
    docker -v
    docker-compose -v
else
    echo "ERROR docker and/or docker-compose not installed, please install docker and docker compose"
    echo "aborting installation"
    exit
fi

KEY_FILE=auth/key.pem
CERT_FILE=auth/cert.pem
if [ ! -f "$KEY_FILE" ] || [ ! -f "$CERT_FILE" ]; then
    echo "ERROR missing certificates for nginx proxy"
    echo "please create a $CERT_FILE and $KEY_FILE accordingly"
    echo "aborting installation"
    exit
fi

docker-compose up -p $QP_DOCKER_PROJECT -d

printf "\n - Check if queue is running by typing 'docker ps' into the command line \n"