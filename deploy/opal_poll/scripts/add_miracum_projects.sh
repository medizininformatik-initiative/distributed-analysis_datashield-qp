#!/bin/bash

source /etc/dsqp/.env
len=${#MIRACUM_PROJECTS[@]}


printf "Creating miracum projects - note: the miracum import user will get permission to administer the projects"

for (( i=0; i<$len; i++ )); 
    do 

        PROJECT=${MIRACUM_PROJECTS[$i]}
        docker exec datashield_opal bash -c "/miracum/init_miracum_project.sh $PROJECT"
    done
