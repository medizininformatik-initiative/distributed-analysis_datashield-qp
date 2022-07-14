#!/bin/bash
source .env

printf "######################\Stopping Opal, Datashield and RServer ...\n######################\n\n"
docker-compose -p $QP_DOCKER_PROJECT stop