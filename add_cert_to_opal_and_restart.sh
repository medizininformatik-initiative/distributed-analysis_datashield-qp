export COMPOSE_PROJECT=ds-qp

docker exec datashield_opal bash -c "cd /opt/opal/bin && ./import_opal_cert.sh"

cd ds_opal

docker-compose -p $COMPOSE_PROJECT stop
docker-compose -p $COMPOSE_PROJECT up -d
