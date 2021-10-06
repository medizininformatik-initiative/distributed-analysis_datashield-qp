#!/bin/bash
PROJECT=$1
TABLE=$2
USER=$3

opal perm-table --opal https://localhost:8443 --user  administrator --password  $OPAL_ADMINISTRATOR_PASSWORD --type USER --project $PROJECT --subject $USER  --permission view --add --tables $TABLE



