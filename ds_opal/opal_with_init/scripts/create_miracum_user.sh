#!/bin/bash

USER=$1
AUTH=$2
TYPE=$3


if [ "$TYPE" = "CERT" ]; then
    echo "create user $USER with cert $AUTH"
    opal user --opal https://localhost:8443 --user  administrator --password  $OPAL_ADMINISTRATOR_PASSWORD --add --name $USER --ucertificate $AUTH
else 
    echo "create user $USER with password $AUTH"
    opal user --opal https://localhost:8443 --user  administrator --password  $OPAL_ADMINISTRATOR_PASSWORD --add --name $USER --upassword $AUTH
fi


echo "give user $USER permission to use datashield"
opal perm-datashield --opal https://localhost:8443 --user  administrator --password  $OPAL_ADMINISTRATOR_PASSWORD --type USER --subject $USER --permission use --add





