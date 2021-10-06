COMMAND=$1
PACKAGE_NAME=${2:-""}

docker exec datashield_rserver bash -c "cd /ds_dev && ./ds_server_admin_server.sh $COMMAND $PACKAGE_NAME"

