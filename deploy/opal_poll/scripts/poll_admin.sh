#!/bin/bash

COMMAND=$1
QUEUE_SERVER=${2:-""}
OPAL_SERVER=${3:-"-o datashield_opal:8443"}
POLL_THREADS=${4:-""}
CHECK_SERVER_CERT=${5:-""}

case "$COMMAND" in
        start )
            echo "Starting poll  with queue server: $QUEUE_SERVER, opal server: $OPAL_SERVER and number of poll threads: $POLL_THREADS"
            docker exec -dit poll_server bash -c "/home/dspoll/poll_admin.sh start '$QUEUE_SERVER' '$OPAL_SERVER' '$POLL_THREADS' '$CHECK_SERVER_CERT'"
            ;;
        
        stop )
            echo "Stopping poll ..."
            docker exec -it poll_server bash -c "/home/dspoll/poll_admin.sh stop"
            ;;

        status )
            docker exec -it poll_server bash -c "/home/dspoll/poll_admin.sh status"
            ;;
        
        * )
            echo $"Usage: $0 {start|stop|status|}"
            exit 1

esac
