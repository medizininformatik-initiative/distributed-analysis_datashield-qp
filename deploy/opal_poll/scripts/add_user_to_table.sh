#!/bin/bash

PROJECT=$1
TABLE=$2
USER=$3


printf "Givign user $USER permission to access table $TABLE of project $PROJECT \n\n "

docker exec datashield_opal bash -c "/miracum/add_user_to_table.sh $PROJECT $TABLE $USER"
