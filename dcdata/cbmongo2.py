#####################################################################
# cbmongo.py
# This tests the MongoDB interface
# Data is pulled from mongoDB and put into a dict: vms
#  mongoDB is on EBS volume (currently 100GB)
#
# TYPE: python cbmongo.py
#
# Here is the code that writes to the server:
#  https://github.com/cloubrain/vmwaredata
# Multi-user version
# 
# ssh into the server:
#  ssh -i cbopen.pem ec2-user@myhost
# make sure to: chmod 400 *.pem
#
# RabbitMQ vizualization:
# http://myhost:15672/
# user: guest
# pass: guest
#
#####################################################################

import os
import sys
import time
import pymongo

# This host has about a day of data in mongoDB
myhost = "ec2-54-234-14-163.compute-1.amazonaws.com"
print "***************"
print "myhost = " + myhost
print "***************"

dbname = "vmware"
statscollname = "stats_new"

dbcon = pymongo.Connection(myhost)		       	# opens connection to the DB
dbpointer = dbcon[dbname]			      	# selects the DB as dbname
dbstatscoll = dbpointer[statscollname]			# selecting the relevant collection

def getClusters():
	return dbpointer.vm.distinct('DCname')

print "*** Print all cluster names ***"
clusters = getClusters()
print clusters
print clusters[1]
DCname = "dkan-cluster-1-dc-19"			#DC name for which you want to extract

#print "*** Print DB ***"
# Just print the whole contents of the DB ordered by earliest timestamp to latest
#cur = dbstatscoll.find().sort([("time_current",1)])	# selecting everything from the collection and sorting by time_current
#cur = dbstatscoll.find()
#for c in cur:				       		# iterating over the cursor
#	print c		       		       	       	# printing everything

print "***************"
print "*** Store DB to vms dict: Takes time to transfer ***"
statresp = dbpointer.command({'dbstats': 1})
print statresp
print "DB Storage Size in GBs:", float(statresp["storageSize"])/(1024*1024*1024)
print "DB File Size in GBs:", float(statresp["fileSize"])/(1024*1024*1024)
#raw_input()

# The DB has a lot of info about many Virtual Machines (VMs)
vmdb = dbpointer["vm"]
vms = {}	
print "*** List of VMs in DCcluster (" + DCname + "):"		       			#main data structure
for vm in vmdb.find({"DCname" : DCname}):
	vms[vm["name"].strip()] = []			#storing all VMs ID into this dict

numvms = len(vms)
print "*** # VMs in cluster:", numvms, "***"

perfkeysdb = dbpointer["perfCounterIdMap"]
perfkeys = {}
for pk in perfkeysdb.find({"DCname": DCname}):
	perfkeys[pk["k"]] = pk["v"]	       	#storing (mapping) all performance metrics' keys with their name here


print "*** Extracting Data from DB ***"
cnt = 0
print "* Progress..."
for c in dbstatscoll.find({"DCname":DCname}):
	cnt += 1
	if cnt%100000 is 0:
		print cnt/100000  # Progress indicator

	r = c
	try:
		r["perfkey"] = perfkeys[c["key"]]
		vms[c["name"]].append(r)			#storing the stats for vm in "vms" dict
	except:
		pass
	

print "***************"
print "*** Print VMs from StatStore ***"
# Sorted by VM
vmcount = 0   # VM counter
for vm in vms:
	vmcount += 1    # vmcount increment for each VM
	stcount = 0    # timestamp counter
	t = []
	#tm = time.time()
	for st in vms[vm]:
		stcount += 1
		t.append(st["perfkey"] + ":" + str(st["value"]))
		tm = st["time_current"]
		t.append("time:" + str(tm) + ":")  # time is added after each data entry
	#print vm, "::", ":".join(t)
	print "******"
	print vm, "::", ":".join(t)
	#print vm
	#print "*" , "::", vm, ":", ":".join(t)
	#print "DBtime: ", tm , "::", vm, ":", ":".join(t)
	stcount = stcount / 2     # We collect cpu,mem. The stcount above is incrementing for each.
	print "*** data history count:", stcount

print "***************"
print "VMcount: " , vmcount

print "***************"
print "Done!"
print "***************"

