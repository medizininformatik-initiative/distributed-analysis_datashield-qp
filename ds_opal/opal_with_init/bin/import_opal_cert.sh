#!/bin/bash

OPAL_ADMIN_PASS=${OPAL_ADMINISTRATOR_PASSWORD:-"password"}

OPAL_KEY=$(sed -E ':a;N;$!ba;s/\r{0,1}\n/\\n/g' /opt/opal/auth/opalkey.pem)
OPAL_CERT=$(sed -E ':a;N;$!ba;s/\r{0,1}\n/\\n/g' /opt/opal/auth/opalcert.pem)

./wait-for-it.sh localhost:8443 -t 120

echo "{\"alias\":\"https\",\"keyType\":\"KEY_PAIR\", \"privateImport\": \"$OPAL_KEY\", \"publicImport\" :\"$OPAL_CERT\"}" | opal rest --opal https://localhost:8443 -u administrator -p $OPAL_ADMIN_PASS --content-type 'application/json' -m PUT /system/keystore