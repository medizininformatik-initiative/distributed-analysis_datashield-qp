echo "Generating Certificat Authority and certificates for development"


openssl req -config cacert.cnf -extensions v3_ca -days 3650 -new -x509 -keyout ./ca_cert/ds_develop_ca.key -out ./ca_cert/ds_develop_ca.crt -nodes
