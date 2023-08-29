#!/bin/bash

source .env

printf "######################\Stopping Poll ...\n######################\n\n"

docker-compose -p $QP_DOCKER_PROJECT stop