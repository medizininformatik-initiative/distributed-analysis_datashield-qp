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
    wget -N "https://gitlab.miracum.org/miracum/uc2/datashield/ds_develop/raw/$VERSION/deploy/opal_poll/docker-compose.yml"
elif [ -n "$QP_HOME_DIR" ]; then
    printf "****\n no version specified updating with data from this folder \n"
    printf "****\n note that config and data files will be kept - if config files have changed you have to transfer them manually\n"
    printf "**** Creating directories and copying files...\n\n"

    mkdir -p $QP_DATA_DIR
    mkdir -p /etc/dsqp/miracum_users
    mkdir -p /etc/dsqp/scripts
    cp $QP_HOME_DIR/docker-compose.yml /etc/dsqp/docker-compose.yml
    cp $QP_HOME_DIR/start.sh /etc/dsqp/start.sh
    cp $QP_HOME_DIR/stop.sh /etc/dsqp/stop.sh
    cp $QP_HOME_DIR/update.sh /etc/dsqp/update.sh
    cp -R $QP_HOME_DIR/scripts/* /etc/dsqp/scripts

else
    printf "\n no version and no install dir given => not doing anything"
    exit

fi

cd /etc/dsqp

docker-compose down
docker-compose up -d

printf "\n - visit your server IP or domain + port 8787 in your browser to access the analysis client \n"


printf "\n the first time opal starts it takes a while to be ready as we are loading test data and configuring the servers for you, so please be patient\n"

printf "\n - visit $OPAL_SERVER_IP:8443 in your browser to access the poll server user interface \n"
printf "\n - visit https://$OPAL_SERVER_IP:443 in your browser to access the opal server user interface \n"
