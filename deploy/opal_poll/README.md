# DS Q-P + OPAL installation guide


## Install your poll thread, opal server and poll monitor server on a server

The Q-P datashield opal application comes packed in docker images, which are automatically donwloaded from your registry of choice.

*Please note that in order to run your poll thread you require a datashield queue server to connect to, so make sure u have installed this before you continue.*

### To install the system:

*open the opal_poll.config file and change the configuration information* to your server requirements.

then execute `./install_prod_opal_poll.sh` in this repo.

Thats it, your poll server, opal and datashield server is now installed.

Please be aware that the server might take a couple of minutes to be available as the startup script automatically installs test data and updates the opal server.


### The config file explained

Your installation package will be already configured to download the correct version from our docker registry.

The most important parameters you will have to change are:
**OPAL_SERVER_IP**,**OPAL_ADMIN_PASS**,**POLL_QUEUE_SERVER**, the rest can stay as is.

- export **OPAL_SERVER_IP**='127.0.0.1' # Ip address of this server (the server which hosts the opal and poll thread) - default is localhost
- export **OPAL_ADMIN_PASS**='password'  # password for the opal server - it is important for this password to be a save password, we suggest using for example `pwgen -sy 20 1` on your command line to generate a safe password
- export **R_SERVER_HOST**='datashield_rserver' # host of an r server used for the opal processing of analysis requests
- export **OPAL_MONGODB_HOST**='datashield_mongo' # host of the mongo database used

- export **POLL_QUEUE_SERVER**='' # e.g. '123.12.12.12:443' , queue server host and port(usually 443), the -q prefix is important. If you have a valid certificate and domain you will need to put the domain here instead of IP
- export **POLL_OPAL_SERVER**=''  # e.g. '123.12.12.12:443' , opal server host and port, if left blank defaults to '-o datashield_opal:8443', which is correct for a pure docker setup
- export **POLL_THREADS**=''      # e.g. '5' number of poll threads defaults to 2
- export **CHECK_SERVER_CERT**='' # e.g. '-c' activate checking sever certificate - this adds extra security, however this results in your poll mechanism not working if your certificate is not correct or you have configured the *POLL_QUEUE_SERVER* using the IP


### Installing your own ssl certificate


**Certificate Opal Server**
To install your own ssl certificate for opal you can either use the user interface or the command line tools we have provided

- command line tools:
1. exchange the opalcert.pem and opalkey.pem files with your own certificate files, but make sure, that the filename stays the same.
2. execute `./import_certificate.sh` in the opal_poll folder (NOT the one in the ./auth folder)
3. your certificate should now be updated

- opal user interface
go to your opal server https://OPAL_SERVER_IP:443 and login as administrator using the password you set in the opal_poll.config file.

**Intermediate Certificate Poll Server**

*DO NOT CONTINUE HERE IF YOU CHOSE TO NOT ACTIVATE THE **CHECK_SERVER_CERT** OPTION*

Install the needed certificate authority certificates

In order for the poll module to check the certificate of the server, it needs to trust the ca_certificate used by your queue server.
To add a ca_cert (certificate authority ssl certificate) proceed as follows:
1. open the ./auth/ca_certs folder and replace the opalcacert.crt and the queuecacert.crt with your own ca cert files.
2. execute the ./addCaCertificates.sh  - your certificates should now be installed on your local machine
