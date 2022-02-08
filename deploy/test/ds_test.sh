#!/bin/bash

# this scripts installs the queue server for you
source .env

REGISTRY_PREFIX=${QP_DOCKER_REGISTRY_PREFIX:-""}
QP_VERSION_TAG=${QP_VERSION_TAG:-""}
QP_QUEUE_HOST=${QP_QUEUE_HOST:-"https://nginx_queue:443/queue"}

if [ -n $QP_VERSION_TAG ]; then
    QP_VERSION_TAG=":$QP_VERSION_TAG"
fi


printf "pulling test container docker image ...\n"

printf "pulling image: $REGISTRY_PREFIX/ds_test$QP_VERSION_TAG \n"
docker pull $REGISTRY_PREFIX/ds_test$QP_VERSION_TAG
docker tag $REGISTRY_PREFIX/ds_test$QP_VERSION_TAG ds_test:latest


docker run -a stdout -e "QUEUE_HOST=$QP_QUEUE_HOST" --rm ds_test:latest