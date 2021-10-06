#!/bin/bash
set -e

TIMEOUT_QUEUE_AND_POLL=${TIMEOUT_QUEUE_AND_POLL:-"100:100"}
LOG_LEVEL=${LOG_LEVEL:-"-l 20"}

if [ -n "$ALLOWED_IPS" ]; then
    ALLOWED_IPS="-c $ALLOWED_IPS"
fi

printf "starting queue server with following command: python3 ds_queue.py -a 0.0.0.0 -p 443 -i -s  -t $TIMEOUT_QUEUE_AND_POLL $ALLOWED_IPS $LOG_LEVEL"
python3 ds_queue.py -a 0.0.0.0 -p 443 -i -s -t $TIMEOUT_QUEUE_AND_POLL $ALLOWED_IPS -l $LOG_LEVEL
