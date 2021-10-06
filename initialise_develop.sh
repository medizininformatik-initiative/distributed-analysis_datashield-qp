#!/bin/bash

cd cert
bash reset_certs.sh
bash create_dev_ca.sh
bash create_dev_do_certs.sh
cd ..
bash start_develop.sh
bash add_certificate_acceptance.sh
bash add_cert_to_opal_and_restart.sh