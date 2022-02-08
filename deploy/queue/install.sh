#!/bin/bash

# this scripts installs the queue server for you
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


printf "**** Creating directory /etc/dsqp for config files and copying unzipped config files to /etc/dsqp directory ...\n\n"
mkdir -p /etc/dsqp/auth
mkdir /etc/dsqp/nginx
mkdir -p $QP_DATA_DIR
cp $QP_HOME_DIR/.env /etc/dsqp/.env
cp $QP_HOME_DIR/docker-compose.yml /etc/dsqp/docker-compose.yml
cp $QP_HOME_DIR/start.sh /etc/dsqp/start.sh
cp $QP_HOME_DIR/stop.sh /etc/dsqp/stop.sh
cp $QP_HOME_DIR/update.sh /etc/dsqp/update.sh
cp -R $QP_HOME_DIR/auth/queue.pem /etc/dsqp/auth/queue.pem
cp -R $QP_HOME_DIR/nginx/* /etc/dsqp/nginx

printf "**** removing config files from home repository $QP_HOME_DIR...\n\n"
rm $QP_HOME_DIR/.env
rm -rf $QP_HOME_DIR/auth
rm -rf $QP_HOME_DIR/nginx

FILE=/etc/dsqp/nginx/dhparam.pem
if [ ! -f "$FILE" ]; then
    echo "Creating longer Diffie-Hellman Prime for extra security... this may take a while \n\n"
    openssl dhparam -out /etc/dsqp/nginx/dhparam.pem 4096
fi

CERT_FILE=/etc/dsqp/auth/queuecert.pem
KEY_FILE=/etc/dsqp/auth/queuekey.pem
if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "ERROR missing certificates for nginx proxy"
    echo "please create a $CERT_FILE and $KEY_FILE accordingly"
    echo "aborting installation"
    exit
fi

cd /etc/dsqp

docker-compose up -d

printf "\n - check if queue is running by typing 'docker ps' into the command line \n"