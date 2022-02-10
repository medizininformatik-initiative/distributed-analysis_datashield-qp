# Load DataSHIELD base package
library(dsBaseClient)
library(DSOpal)

# The login data object is a data.frame
builder <- DSI::newDSLoginBuilder()

#builder$append(server="server1", url='http://datashield_opal:8080',
#               user="administrator", password="develop")

#builder$append(server="server1", url='https://nginx_queue:8443',
#               user="administrator", password="develop")

builder$append(server="server1", url='http://queue_server:8443',
               user="administrator", password="develop")

logindata <- builder$build()

# Then perform login in each server
connections <- datashield.login(logins=logindata)


datashield.assign.table(connections, symbol = "D",
                        table = list(server1 = "test.CNSIM1"),
                        variables=list('LAB_GLUC','LAB_HDL'))

mean <- ds.mean(x = 'D$LAB_HDL', type = "combine", datasources = connections)
print(mean)
print(datashield.errors())
