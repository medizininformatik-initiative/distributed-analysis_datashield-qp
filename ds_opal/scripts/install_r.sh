# install r and datashield dev packages
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys E084DAB9

apt-get update && \
apt-get install -y r-base r-base-dev && \
apt-get install -y libcurl4-openssl-dev && \
apt-get install -y libxml2-utils && \
apt-get install -y libxml2-dev

# install opal packages
R -e 'install.packages(c("rjson", "RCurl", "mime"), repos="https://cran.uni-muenster.de/")'
R -e 'install.packages("opal", repos="http://cran.obiba.org", type="source", dependencies=TRUE)'
R -e 'install.packages("opaladmin", repos="http://cran.obiba.org", type="source")'

# install datashield packages
R -e "install.packages('datashieldclient', repos=c('https://cran.uni-muenster.de/', 'http://cran.obiba.org'), dependencies=TRUE)"

# update obiba packages
R -e 'update.packages(repos="http://cran.obiba.org")'