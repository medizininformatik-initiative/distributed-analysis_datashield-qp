#!/bin/bash

export COMPOSE_PROJECT=ds-qp

cd ds_opal
docker-compose -p $COMPOSE_PROJECT down

cd ../ds_poll/deploy
docker-compose -p $COMPOSE_PROJECT down

cd ../../ds_queue/deploy
docker-compose -p $COMPOSE_PROJECT down

printf "Down NGINX for Queue \n"
docker-compose -p $COMPOSE_PROJECT -f docker-compose.nginx.q.yml down

cd ../../ds_simple_client
docker-compose -p $COMPOSE_PROJECT down