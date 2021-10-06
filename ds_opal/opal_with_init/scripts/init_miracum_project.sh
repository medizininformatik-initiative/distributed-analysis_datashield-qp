#!/bin/bash

PROJECT=$1

echo "create project $PROJECT "

echo "{\"name\":\"$PROJECT\",\"title\":\"$PROJECT\", \"database\": \"miracum\"}" | opal rest --opal https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD --content-type 'application/json' -m POST /projects

sleep 10

echo "give miracum_import user permission to administrate the project"
opal perm-datasource --opal https://localhost:8443 --user  administrator --password  $OPAL_ADMINISTRATOR_PASSWORD --type USER --subject miracum_import --permission administrate --add --project $PROJECT




