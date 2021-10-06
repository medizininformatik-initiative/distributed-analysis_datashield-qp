cd ca_cert
rm *
touch index.txt
echo "01" >> serial

cd ../do_cert
rm -rf *