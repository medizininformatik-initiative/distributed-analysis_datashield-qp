cd ../ds_test && docker-compose down
cd ../ds_opal
docker-compose -f docker-compose.prod.yml down
rm -rf ds_data
docker network remove ds_opal_opal_net