from ubuntu:latest

#set environment variable to supress user interaction
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
apt-get install gnupg -y

# install r and datashield dev packages
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys E084DAB9

RUN apt-get update && \
apt-get install -y r-base r-base-dev && \
apt-get install -y libcurl4-openssl-dev libssl-dev && \
apt-get install -y libxml2-utils && \
apt-get install -y libxml2-dev && \
apt-get install -y cmake

# install opal packages
RUN R -e "install.packages('DSOpal', repos=c(getOption('repos'), 'https://cran.obiba.org'))" && \
R -e "install.packages('dsBaseClient', repos=c(getOption('repos'), 'https://cran.obiba.org'))"

# update obiba packages
RUN R -e 'update.packages(repos="http://cran.obiba.org")'

