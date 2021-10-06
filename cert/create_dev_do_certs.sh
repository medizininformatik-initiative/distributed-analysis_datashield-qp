echo "Generating Domain Certificates for each component"


#!/bin/sh
certnames=("queue" "poll" "opal" "queuenginx")

for certname in "${certnames[@]}"; do
  CURRENT="do_cert/$certname"
  echo $CURRENT
  openssl req -config "${certname}cert.cnf" -days 365 -nodes -new -keyout $CURRENT.key -out $CURRENT.csr
  openssl ca -batch -notext -config "${certname}cert.cnf" -out $CURRENT.crt -infiles $CURRENT.csr 
  cat $CURRENT.crt $CURRENT.key > $CURRENT.pem
done



