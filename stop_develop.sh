#!/bin/bash

export COMPOSE_PROJECT=ds-qp

cd ds_opal
docker-compose -p $COMPOSE_PROJECT stop

cd ../ds_poll/deploy
docker-compose -p $COMPOSE_PROJECT stop

cd ../../ds_queue/deploy
docker-compose -p $COMPOSE_PROJECT stop

docker-compose -p $COMPOSE_PROJECT -f docker-compose.nginx.q.yml stop

cd ../../ds_simple_client
docker-compose -p $COMPOSE_PROJECT stop