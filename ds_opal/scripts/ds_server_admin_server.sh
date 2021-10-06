COMMAND=$1
PACKAGE_NAME=${2:-""}


function getQueueStatus() {

    if [ "" == "$(pgrep -f queue.py)" ]; then 
        echo "Queue Stopped"
    else
        echo "Queue Running"
    fi
}

case "$COMMAND" in
        install )
            if [ -n "$PACKAGE_NAME" ]; then 
                echo "Installing package $PACKAGE_NAME"
                R -e "if( ! is.element('devtools', installed.packages()[,1]) ) {install.packages('devtools')}; library(devtools) ; devtools::install('/ds_dev/ds_server_funcs/$PACKAGE_NAME')"
            else
                echo "No package name specified => not installing anything"
            fi
            ;;

        status )
            echo "this is the status of the server"
            ;;
        
        * )
            echo $"Usage: $0 {install|status} package_name"
            exit 1

esac
