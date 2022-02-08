#!/bin/bash

USER="miracum_import"
PW=$(pwgen -s 30 1)


docker exec --user=root datashield_opal bash -c "/miracum/init_miracum_import_user.sh $USER $PW"

echo "Created Import User and written user information to /etc/dsqp/miracum_projects.config"
echo "Created User: $USER with password: $PW" >> /etc/dsqp/miracum_projects.config

