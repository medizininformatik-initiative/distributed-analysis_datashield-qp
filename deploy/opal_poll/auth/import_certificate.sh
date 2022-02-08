#!/bin/bash
OPAL_ADMIN_PASS=${OPAL_ADMINISTRATOR_PASSWORD:-"password"}

OPAL_KEY=$(sed -E ':a;N;$!ba;s/\r{0,1}\n/\\n/g' opalkey.pem)
OPAL_CERT=$(sed -E ':a;N;$!ba;s/\r{0,1}\n/\\n/g' opalcert.pem)

echo "{\"alias\":\"https\",\"keyType\":\"KEY_PAIR\", \"privateImport\": \"$OPAL_KEY\", \"publicImport\" :\"$OPAL_CERT\"}" | opal rest --opal https://localhost:8443 -u administrator -p $OPAL_ADMIN_PASS --content-type 'application/json' -m PUT /system/keystore
