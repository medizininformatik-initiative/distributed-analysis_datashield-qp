# DS Q-P + OPAL installation guide


## Install your queue server on a server

The Q-P datashield opal application comes packed in docker images, which are automatically donwloaded from your registry of choice.

### To install the system:

*open the queue.config file and change the configuration information* to your requirements.

then execute `./install.sh` in this repo.

Thats it, your queue server is now installed.

you can check, using your command line, if everything is running by typing `docker ps`. You should now see two running containers (queue_server_prod and nginx_queue)


### Config file explained

Your installation package will be already configured to download the correct version from our docker registry.

The only parameter you should change is the ALLOWED_IPS parameter.

To change remove the "#" from the following config line:

```
# export ALLOWED_IPS='-c 140.0.0.1,140.0.0.1'
```

and change the list of IP addresses to comma-separated list of the IP addresses you would like to allow to access your queue.

Make sure that the list contains at least the IP address of your Poll-Opal server and your DataSHIELD analysis server.

important: the "-c" has to be retained, followed by a space and then the list of allowed IP addresses.



### Install own SSL certificate

The queue server comes with a nginx reverse proxy. This means that two certificates have to be changed. One for the queue and one for the nginx server.

Important: this has to be done after you have installed the queue.


**Certificate nginx reverse proxy:**
1. Open the queuecert.pem and queuekey.pem files in your application config file directory  Applikationsverzeichnis ((`/etc/dsq/nginx`))
2. Delete the respective file contents
3. Insert your own certificate (in queuecert.pem) and key (in queuekey.pem) into the respective files
4. If you are using your own CA (certificate authority) make sure you also paste all the intermediate certificates into your queuecert.pem file


**Certificate queue_server:**
1. open the queue.pem file in your application directory (`/etc/dsq/auth`)
2. delete the content of the queue.pem file
3. Paste your own certificate and private key into the queue.pem file
4. If you are using your own CA (certificate authority) make sure you also paste all the intermediate certificates

After you have changed the certificates **restart the queue** using the `./stop.sh` and `./start.sh` files in your application dir one after another.



