#!/bin/bash

source /etc/dsqp/.env

for user in ${MIRACUM_USERS[@]}
do
   echo $user
   CERT_FILE=/miracum_users/users/$user.pem
   
   if [ -f "$CERT_FILE" ]; then
        docker exec datashield_opal bash -c "/miracum/create_miracum_user.sh $user $CERT_FILE CERT"
    else 
        PW=$(pwgen -s 30 1)
        docker exec datashield_opal bash -c "/miracum/create_miracum_user.sh $user $PW"
        echo "Created new User $user and written user information to /etc/dsqp/miracum_projects.config"
        echo "Created User: $user with password: $PW" >> /etc/dsqp/miracum_projects.config
    fi
   
done
