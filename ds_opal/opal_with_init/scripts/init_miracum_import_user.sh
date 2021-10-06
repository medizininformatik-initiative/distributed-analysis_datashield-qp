#!/bin/bash

USER=$1
PW=$2

echo "create import user $USER "

opal user --opal https://localhost:8443 --user  administrator --password  $OPAL_ADMINISTRATOR_PASSWORD --add --name $USER --upassword $PW

