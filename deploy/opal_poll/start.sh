#!/bin/bash

source .env

printf "######################\n Testing if queue is available before initial startup...\n######################\n\n"

curl -k "https://$POLL_QUEUE_SERVER/?ping=true"
QUEUE_AVAIL=$(curl -k "https://$POLL_QUEUE_SERVER/?ping=true")

if [[ ! $QUEUE_AVAIL == "queue is still alive " ]];then
printf "\n The queue is not available, the following curl ping request failed: curl -k https://$POLL_QUEUE_SERVER/?ping=true\n"
printf "\n Exiting now - reconfigure your variable POLL_QUEUE_SERVER in your .env file in the folder /etc/dsqp and execute the ./start.sh again \n"
exit
fi 


printf "######################\nInitialising Opal and installing Datashield and RServer ...\n######################\n\n"

docker-compose up -d
