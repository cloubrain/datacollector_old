dcdata
======

Type:    python cbmongo.py

Scripts to pull cloud data from mongoDB server.
  Data is pulled from mongoDB and put into a dict
  mongoDB is on EBS volume (currently 100GB)

cbmongo.py
CBmongo class to pull data from mongoDB
See example at bottom for calling CBmongo from your analyzer
testdb()
  Example code to use CBmongo functions
getStats()
  Print DB stats
getClusters()
  Returns all clusterNames in DB
getData(clusterName, start, end)
  Returns dict with all data from given cluster sorted by VM
   clusterName: cluster you want data from
   start: place in time to go back (0=now, 1000=back in time)
   end: number of data points you want
printData(vms) DOES NOT WORK WITH UPDATED getData
  Takes the dict from getData
  Prints data

rabbitmongo.py
  Moves data from RabbitMQ queue to mongoDB on large EBS volume

cbmongo2.py  OLD VERSION not used
  Script to pull data from mongoDB
  Stores data to a dict called: vms
  print vms

cbmongo1.py rabbitmongo1.py
  OLD VERSIONS: not used
