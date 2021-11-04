#!/bin/bash

export COMPOSE_PROJECT=ds-qp

printf "Starting Queue \n"
cd ds_queue/deploy
docker-compose -p $COMPOSE_PROJECT up -d

printf "Starting NGINX for Queue \n"
#docker-compose -p $COMPOSE_PROJECT -f docker-compose.nginx.q.yml up -d

printf "Starting Opal \n"
cd ../../ds_opal
docker-compose -p $COMPOSE_PROJECT up -d

printf "Starting Poll \n"
cd ../ds_poll/deploy
docker-compose -p $COMPOSE_PROJECT up -d

cd ../../ds_simple_client
docker-compose -p $COMPOSE_PROJECT up -d


