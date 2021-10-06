# Load DataSHIELD base package
library(dsBaseClient)
library(DSOpal)

queueHost=Sys.getenv("QUEUE_HOST")

# The login data object is a data.frame
builder <- DSI::newDSLoginBuilder()

builder$append(server="server1", url=queueHost,
               user="test", password="test123")

logindata <- builder$build()

tryCatch(
        {
            message(paste("\n\n###  Begin connecting to DataSHIELD Queue Server with host: ", queueHost, " ###\n\n"))

            connections <- datashield.login(logins=logindata)

            datashield.assign.table(connections, symbol = "D", table = list(server1 = "test.CNSIM1"), variables=list('LAB_GLUC','LAB_HDL'))

            mean <- ds.mean(x = 'D$LAB_HDL', type = "combine", datasources = connections)
            expected_mean = 1.5694163155851399427120895779808051884174346923828125
            
            if(mean[[1]][1] == expected_mean){
                message("\n\nSUCCESS: Congratulations a mean has been succesfully calculated on test data using your DataSHIELD infrastructure\n\n")
            }else {
                message("\n\nERROR: The basic mean calculation using DataSHIELD failed, please check if your servers are all correctly set up!!!\n\n")
            }
        },
        error=function(cond) {
            message(cond)
            message("\n\nERROR: The basic mean calculation using DataSHIELD failed, please check if your servers are all correctly set up!!!\n\n")
            
        }
    )
