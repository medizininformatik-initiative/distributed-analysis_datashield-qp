#!/bin/bash

source .env

while getopts v:d: option
do
case "${option}"
in
v) VERSION=${OPTARG};;
d) QP_HOME_DIR=${OPTARG};;

esac
done

if [ -n "$VERSION" ]; then
    wget -N "https://gitlab.miracum.org/miracum/uc2/datashield/ds_develop/raw/$VERSION/deploy/queue/docker-compose.yml"
elif [ -n "$QP_HOME_DIR" ]; then
    printf "****\n no version specified updating with data from this folder \n"
    printf "****\n note that config and data files will be kept - if config files have changed you have to transfer them manually\n"
    printf "**** Creating directories and copying files...\n\n"

    mkdir -p $QP_DATA_DIR
    cp $QP_HOME_DIR/docker-compose.yml /etc/dsqp/docker-compose.yml
    cp $QP_HOME_DIR/start.sh /etc/dsqp/start.sh
    cp $QP_HOME_DIR/stop.sh /etc/dsqp/stop.sh
    cp $QP_HOME_DIR/update.sh /etc/dsqp/update.sh

else
    printf "\n no version and no install dir given => not doing anything"
    exit

fi

cd /etc/dsqp

docker-compose down
docker-compose up -d

printf "\n - check if queue is running by typing 'docker ps' into the command line \n"
