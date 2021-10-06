#!/bin/bash
set -e

LOG_LEVEL=${LOG_LEVEL:-"20"}
POLL_THREADS=${POLL_THREADS:-"2"}
POLL_OPAL_SERVER=${POLL_OPAL_SERVER:-"datashield_opal:8443"}
OWN_CERT_CA=$OWN_CERT_CA

printf "starting poll server with following command: python3 ds_poll.py -q $POLL_QUEUE_SERVER -o $POLL_OPAL_SERVER -s -l $LOG_LEVEL -t $POLL_THREADS $CHECK_SERVER_CERT"
python3 ds_poll.py -q $POLL_QUEUE_SERVER -o $POLL_OPAL_SERVER -s -l $LOG_LEVEL -t $POLL_THREADS $OWN_CERT_CA
