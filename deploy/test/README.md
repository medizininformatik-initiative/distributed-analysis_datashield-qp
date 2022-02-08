# DS SETUP Test guide

The Q-P datashield opal application comes packed in docker images, which are automatically donwloaded from your registry of choice.
Using this test package assumes that you have just installed the Q-P DataSHIELD extension with the Opal server and the respective DataSHIELD packages.

## How to use:

To test your installation we ahave provided a test docker container, which has the respective DataSHIELD client packages installed.
This container will start up and execute ad DataSHIELD test script and then remove itself again.

It can be started on any machine which has been granted access to the queue server during the queue server installation.

One machine you can potentially use (given correct firewall rights) is the opal_poll server you have installed previously.

Go to the directory you have unpacked this repository to, then

*open the test.config file and change the configuration information* to your requirements.

then execute `./ds_test.sh` in this repo.

If your installation works correctly you will see a "SUCCESS" message on your command line.


### Config file explained

Your installation package will be already configured to download the correct version from our docker registry.

The only parameter you should change is the export QP_QUEUE_HOST parameter:

Change the host to your queue host (IP or domain, if applicable) and port

export QP_QUEUE_HOST='https://nginx_queue:443' # change queue host to your host



