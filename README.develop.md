# ds_develop

See main README file of this repository before reading on.

This README guides you through how you can participate in the development of this repository and how to setup your own development environment.

## Install Docker

1. Install docker, if you are using linux ubuntu you can simply execute the build_from_images/install_docker.sh of this repository, else 
   please refer to https://www.docker.com/get-started 

2. Install docker-compose (note: the install_docker.sh script install docker-compose for you)


## initialise your develop environment and start all neccessary docker containers

To initialise your development environment you can use the `initialise_develop.sh` provided in this repository.

This
1. Creates a certificate authority (CA) and ssl certificates for each component
2. starts up the development environment
3. adds the newly created CA to each components allowed CAs
4. Uploads the opal certificate to opal and restarts opal in order for the new certificate to take effect.

This results in a development environment with all the neccessary components on localhost, communicating via https within the same docker network for development purposes.
This development environment should not be used for production.

It spins up the following components (see diagram below):

datashield_datashield: A Simple datashield client, which can be used inside the docker container to execute datashield scripts
poll_server: the poll component of the infrastructure
queue_server: the queue component of the infrastructure
datashield_opal: the opal datawarehouse responsible for storing the patient data for datashield
datashield_mongo: the database for opal
ds-qp_rock1_1: An R execution Server used by Opal to execute the datashield requests on the data
ds-qp_rock2_1: An R execution Server used by Opal to execute the datashield requests on the data

![DS-QP Develop Overview](img/ds-qp-develop.png?raw=true "Overview DS-QP Development Environment")


## Start developing

Visit your browser on localhost to access your Opal datawarehouse application: <http://localhost:8880/ui/index.html>
If you are not familiar with Opal and DataSHIELD, please refer to the official documentation: <https://opaldoc.obiba.org/en/latest/cookbook/index.html>


### Start your Queue Server

`docker exec -it queue_server bash`
`python3 ds_queue.py -a 0.0.0.0 -p 443 -i -t 10:10 -l 10`

The files of the queue server are mounted to the queue_server docker container:
=> When you change files in the ds_queue folder of this repository, stop your queue application inside the docker container and then start it again, 
the queue application will run with your changes

### Start your Poll Application

`docker exec -it poll_server bash`
`python3 ds_poll.py -q queue_server:443 -o datashield_opal:8080 -l 10 -t 2`

The files of the poll server are mounted to the poll_server docker container:
=> When you change files in the ds_poll folder of this repository, stop your poll application inside the docker container and then start it again, 
the poll application will run with your changes.

### Enter your simple datashield client and send a request via the queue and poll

`docker exec -it ds_simple_client bash`
`cd /testscript`
`Rscript datashield_test.r`

The scripts inside the ds_test/testcript folder  are mounted to the ds_simple_client  docker container:
=> When you change files in testcript folder of this repository, and run the Rscript inside the docker container, 
the Script will automatically contain the newest changes you have made.
