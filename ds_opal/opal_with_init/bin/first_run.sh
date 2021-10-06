#!/bin/bash

# Configure some databases for IDs and data
if [ -n "$MONGO_PORT_27017_TCP_ADDR" ]
	then
	echo "Initializing Opal databases with MongoDB..."
	if [ -z "$MYSQLIDS_PORT_3306_TCP_ADDR" ]
		then
		sed s/@mongo_host@/$MONGO_PORT_27017_TCP_ADDR/g /opt/opal/data/mongodb-ids.json | \
    		sed s/@mongo_port@/$MONGO_PORT_27017_TCP_PORT/g | \
    		opal rest -o https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD -m POST /system/databases --content-type "application/json"
    fi
	sed s/@mongo_host@/$MONGO_PORT_27017_TCP_ADDR/g /opt/opal/data/mongodb-data.json | \
    	sed s/@mongo_port@/$MONGO_PORT_27017_TCP_PORT/g | \
    	opal rest -o https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD -m POST /system/databases --content-type "application/json"
fi


# Configure standard Mongo Db Connection
if [ -n "$MONGODBHOST" ]
	then
	echo "initialising mongo db with ids and data"
	echo "{\"name\": \"_identifiers\", \"defaultStorage\":false, \"usage\": \"STORAGE\", \"usedForIdentifiers\":true, \"mongoDbSettings\" : {\"url\":\"mongodb://$MONGODBHOST:27017/opal_ids\"}}" | opal rest --opal https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD --content-type 'application/json' -m POST /system/databases 
	echo "{\"name\":\"miracum\",\"defaultStorage\":false, \"usage\": \"STORAGE\", \"mongoDbSettings\" : {\"url\":\"mongodb://$MONGODBHOST:27017/opal_data\"}}" | opal rest --opal https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD --content-type 'application/json' -m POST /system/databases
fi

# Configure datashield packages
if [ -n "$ROCK_HOSTS" ] || [ -n "$RSERVER_HOST" ]
	then
	echo "Initializing Datashield default profile..."
	opal rest -o https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD -m PUT /datashield/packages/_publish
	opal rest -o https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD -m PUT /datashield/profile/default/_enable
fi


if [ "$INITTESTDATA" == "true" ]
	then

  echo "Initialising test data, as initialisation is set to true"

	echo "Create a test project..."
	echo '{"name":"test","title":"test", "database": "miracum"}' | opal rest --opal https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD --content-type 'application/json' -m POST /projects

	echo "Upload the needed test files files..."
	opal file --opal https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD -up /testdata/CNSIM/CNSIM.zip /projects
	opal file --opal https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD -up /testdata/DASIM/DASIM.zip /projects

	echo "Import the CNSIM and DASIM test files to the test project..."
	opal import-xml --opal https://localhost:8443 --user administrator --password $OPAL_ADMINISTRATOR_PASSWORD --path /projects/CNSIM.zip --destination test
	opal import-xml --opal https://localhost:8443 --user administrator --password $OPAL_ADMINISTRATOR_PASSWORD --path /projects/DASIM.zip --destination test

	echo "Create a test user..."
	opal user --opal https://localhost:8443 --user  administrator --password  $OPAL_ADMINISTRATOR_PASSWORD --add --name test --upassword test123
	sleep 10

	echo "Give test user permission to access CNSIM1 table"
	opal perm-table --opal https://localhost:8443 --user  administrator --password  $OPAL_ADMINISTRATOR_PASSWORD --type USER --project test --subject test  --permission view --add --tables CNSIM1

	echo "Give test user permission to use datashield"
	opal perm-datashield --opal https://localhost:8443 --user  administrator --password  $OPAL_ADMINISTRATOR_PASSWORD --type USER --subject test --permission use --add

  echo "Sleeping 30 seconds to give opal some time to copy all files..."
fi

if [ -n "$DS_VERSION" ]
  then

echo "Installing datashield packages version = $DS_VERSION..."
opal rest --opal https://localhost:8443 --user  administrator --password  $OPAL_ADMINISTRATOR_PASSWORD -m POST "/datashield/packages?name=dsBase&profile=default"
fi

if [ -n "$DS_PRIVACY_LEVEL" ]
  then
  
  printf "Setting datashield privacy level to: $DS_PRIVACY_LEVEL \n"
  echo "{name: \"datashield.privacyLevel\", value: \"$DS_PRIVACY_LEVEL\"}" | opal rest --opal https://localhost:8443 -u administrator -p $OPAL_ADMINISTRATOR_PASSWORD --content-type 'application/json' -m POST /datashield/option
fi

printf "\n##########\n Finished setup for first run - Opal is ready to use now \n##########\n"



