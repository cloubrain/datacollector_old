#####################################################################
# cbmongo.py
# This tests the MongoDB interface
# Data is pulled from mongoDB and put into a dict: vms
#
# TYPE: python cbmongo.py
#
# Here is the code that writes to the server:
#  https://github.com/cloubrain/datacollector/tree/master/vmware
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

# This host is the data collection host
myhost = "ec2-54-234-14-163.compute-1.amazonaws.com" # Live data streaming to this server
print "***************"
print "myhost = " + myhost
print "***************"

dbname = "vmware"
statscollname = "stats_new"
dbcon = pymongo.Connection(myhost)		       	# opens connection to the DB
dbpointer = dbcon[dbname]			      	# selects the DB as dbname
dbstatscoll = dbpointer[statscollname]			# selecting the relevant collection

#print "*** Print DB ***"
# Just print the whole contents of the DB ordered by earliest timestamp to latest
#cur = dbstatscoll.find().sort([("time_current",1)])	# selecting everything from the collection and sorting by time_current
#cur = dbstatscoll.find()
#for c in cur:				       		# iterating over the cursor
#	print c		       		       	       	# printing everything

#print "***************"
print "*** Store DB to vms dict: Takes time to transfer ***"
#print "*** DB stats: ~2s/MB ***"
#statresp = dbpointer.command({'dbstats': 1})
#print statresp

# The DB has a lot of info about many Virtual Machines (VMs)
vmdb = dbpointer["vm"]

vms = {}			       			#data structure for VM data
for vm in vmdb.find():
	vms[vm["name"].strip()] = []			#storing all VMs ID into this dict

numvms = len(vms)
print "*** # VMs in DB:", numvms, "***"

perfkeysdb = dbpointer["perf_counter_id_map"]
perfkeys = {}
for pk in perfkeysdb.find():
	perfkeys[pk["key"]] = pk["value"]	       	#storing (mapping) all performance metrics' keys with their name here

numpk = len(perfkeys)
print "*** # perf keys:", numpk, "***"
print "*** Extracting Data from DB ***"
cnt = 0
print "* Progress..."
for c in dbstatscoll.find():
	cnt += 1
	if cnt%100000 is 0:
		print cnt/100000  # Progress indicator

	r = c
	try:
		r["perfkey"] = perfkeys[c["key"]]
		vms[c["name"]].append(r)		#storing the stats for vm in "vms" dict
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
	for st in vms[vm]:
		stcount += 1
		t.append(st["perfkey"] + ":" + str(st["value"]))
		tm = st["time_current"]
		t.append(":Time:" + str(tm))
	print "******"
	print vm, "::", ":".join(t)
	#print vm
	print "*** data history count:", stcount
	#print "*" , "::", vm, ":", ":".join(t)

print "***************"
print "VMcount: " , vmcount

print "***************"
print "Done!"
print "***************"
