# Dockerized deployment of qp together with dataSHIELD 

**This is just a sketch now to depict the proposal of the new structure in the deployment folder**

## Prerequisites

- Install Docker and docker-compose in the current version
- Including the dataSHIELD Opal server, the qp extension consists of four different components (see publication). Running them all on one machine would make qp pointless. Please plan which components will run on which machine before start installing. 
- Checkout this repository to your machine.

### Server certificates and keys
You will need a key and a certificate for each of three of the Docker containers (queue server, NGINX for queue server, Opal server). These can be either regular trusted keys or keys trusted be a newly created Certificate Authority (CA), thus self-singed one. To create an own CA and own keys you can use the scripts in the folder `cert`. Self-signed or regular, the keys and certificates need to be placed in the folder `cert/do_cert`. If an own CA is used, please ensure that this CA is added to the certificate store of the docker container (**TODO** Use existing methods to add automatically).

## Deployment of different components
### Queue server
1. Change to folder `deployment/ds_queue`
2. Edit the file `.env` and set the parameter `ALLOWED_IPS` to allowed IPs and subnets separated by a comma. The parameter should contain all allowed client IPs as well as the IPs of the poll server.
3. Ensure the files `queue.key` and `queue.crt` are filled with the correct key and certificate.
4. Start the queue server with the command `docker-compose up -d`

### NGINX for queue server
1. Change to folder `deployment/ds_queue`
2. Set the parameter `ALLOWED_IPS` in the file `.env`. You probably maybe already did this in the deployment of the queue server.
3. Ensure the files `queuenginx.key` and `queuenginx.crt` are filled with the correct key and certificate.
4. Start the NGINX server with the command `docker-compose -f docker-compose.nginx.q.yml up -d`

### Poll server
1. Change to folder `deployment/ds_poll`
2. Set the parameters `POLL_QUEUE_SERVER` and `POLL_OPAL_SERVER` in the file `.env` to the domain and ports of the queue server and the opal server.
3. Start the poll server with the command `docker-compose up -d`
### Opal server
The file `deployment/ds_opal/docker-compose.yml` contains a sample docker-compose file taken from the Opal documentation. Be sure to adapt it to your needs and change the administrator password.
1. Change to folder `deployment/ds_opal`
2. Start the opal server with the command `docker-compose up -d`

## Troubleshooting
### Error reading certificates
The keys must be readable to the users of the Docker containers, which are not always root. In the containers' logs you may find messages indicating that the keys files are not readable. To enable reading the keys, you can make them readable with `chmod o+r <file>`. However, in this case everybody on your system can access the key files. In order to restrict access you can change the owner of the file in the host system to the id of the running user in the Docker container, even if that user does not exists on the host system. For instance, execute `sudo chown 101:101 queuenginx.key` to allow the NGINX key to be read by the container.

### Error writing queue_allow_ips.conf file
The NGINX container creates a file queue_allow_ips.conf at the beginning, which is stored in the folder `deploy/ds_queue/nginx` on your host system. If the Docker logs of the NGINX container put out a message like `/etc/nginx/conf.d/queue_allow_ips.conf: Permission denied` you can try to delete the file and restart the container. Also check whether the NGINX container can write to the folder `deploy/ds_queue/nginx`. 
