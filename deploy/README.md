# Dockerized deployment of qp together with DataSHIELD 

## Prerequisites

- Install Docker and docker-compose in the current version
- Including the DataSHIELD Opal server, the qp extension consists of four different components (see publication).
- Checkout this repository to your machine.

### Server certificates and keys
You will need a key and a certificate for each of three of the Docker containers (queue server, NGINX for queue server, Opal server). These can be either regular trusted keys or keys trusted by a newly created Certificate Authority (CA), thus self-singed ones. To create your own CA and own keys you can use the scripts in the folder `cert`. Self-signed or regular, the keys and certificates need to be placed in the folder `cert/do_cert`. If your own CA is used, please ensure that this CA is added to the certificate store of the docker container.

Note that self-signed certificates should only be used for develop.

## Deployment of different components

### Queue server and NGINX

1. Change to the folder `deploy` of this repository
2. Execute the `init-env-files.sh`
3  Change to the folder `queue` of this repository
4. Edit the file `.env` and set the parameter `ALLOWED_IPS` to allowed IPs and subnets separated by a comma. The parameter should contain all allowed client IPs as well as the IPs of the poll server.
5. Add your certificates to the auth folder as `key.pem` and `cert.pem` files.
6. Start the queue server and the nginx using the `start.sh` script of the `queue` folder

### Poll server
1. Change to the folder `deploy` of this repository.
2. Execute the `init-env-files.sh`.
3  Change to the folder `poll` of this repository.
4. Set the parameters `POLL_QUEUE_SERVER` and `POLL_OPAL_SERVER` in the file `.env` to the domain and ports of the queue server and the opal server.
5. Add your certificates to the auth folder as `key.pem` and `cert.pem` files.
6. Start the poll application using the `start.sh` script of the `poll` folder.

### Opal server
1. Change to the folder `deploy` of this repository.
2. Execute the `init-env-files.sh`.
3  Change to the folder `opal` of this repository.
4. Edit the file `.env`: Set the parameter `OPAL_ADMIN_PASS` and choose a safe password.
5. Add your certificates to the auth folder as `key.pem` and `cert.pem` files.
6. Start the opal server and the nginx using the `start.sh` script of the `opal` folder.
7. To add a certificate to OPAL its easiest to open the ADMIN console <your-opal-domain> and login as admin. Then click `General Settings` > `Set Key Pair` > `Import Key Pair` and paste your key and certificate in the respective fields and click `save`. 
8. After adding your certificate for it to take effect you need to restart your opal server by first executing the `stop.sh` followed by the `start.sh` of the `opal` folder.

## Troubleshooting
### Error reading certificates
The keys must be readable to the users of the Docker containers, which are not always root. In the containers' logs you may find messages indicating that the keys files are not readable. To enable reading the keys, you can make them readable with `chmod o+r <file>`. However, in this case everybody on your system can access the key files. In order to restrict access you can change the owner of the file in the host system to the id of the running user in the Docker container, even if that user does not exists on the host system. For instance, execute `sudo chown 101:101 queuenginx.key` to allow the NGINX key to be read by the container.

### Error writing queue_allow_ips.conf file
The NGINX container creates a file queue_allow_ips.conf at the beginning, which is stored in the folder `deploy/ds_queue/nginx` on your host system. If the Docker logs of the NGINX container put out a message like `/etc/nginx/conf.d/queue_allow_ips.conf: Permission denied` you can try to delete the file and restart the container. Also check whether the NGINX container can write to the folder `deploy/ds_queue/nginx`.
