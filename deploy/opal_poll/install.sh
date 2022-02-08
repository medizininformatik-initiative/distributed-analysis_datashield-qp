#!/bin/bash

source .env
QP_HOME_DIR=${QP_HOME_DIR:-"$PWD"}


if [[ $(which docker) && $(which docker-compose) ]]; then
    echo "docker and docker compose already installed, versions are: "
    docker -v
    docker-compose -v
else
    echo "ERROR docker and/or docker-compose not installed, please install docker and docker compose"
    echo "aborting installation"
    exit
fi

printf "**** Creating directory /etc/dsqp for config files and copying config files to /etc/dsqp directory ...\n\n"
mkdir -p $QP_DATA_DIR
mkdir -p /etc/dsqp/auth
mkdir -p /etc/dsqp/miracum_users
mkdir -p /etc/dsqp/scripts
cp $QP_HOME_DIR/.env /etc/dsqp/.env
cp $QP_HOME_DIR/docker-compose.yml /etc/dsqp/docker-compose.yml
cp $QP_HOME_DIR/start.sh /etc/dsqp/start.sh
cp $QP_HOME_DIR/stop.sh /etc/dsqp/stop.sh
cp $QP_HOME_DIR/update.sh /etc/dsqp/update.sh

cp -R $QP_HOME_DIR/auth/* /etc/dsqp/auth
cp -R $QP_HOME_DIR/miracum_users/* /etc/dsqp/miracum_users
cp -R $QP_HOME_DIR/scripts/* /etc/dsqp/scripts


cd /etc/dsqp

./start.sh

printf "\n the first time opal starts it takes a while to be ready as we are loading test data and configuring the servers for you, so please be patient\n"

printf "\n - visit https://$OPAL_SERVER_IP:443 in your browser to access the opal server user interface \n"
