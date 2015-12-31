#####################################################################
# cbmongo.py
# cbmongo class gets data from mongoDB on our server
#
# TYPE: python cbmongo.py
#  Example code at bottom
#
# CBmongo class to pull data from mongoDB
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
# Copyright (C) 2013 by Cloubrain, Inc.
# Pete C. Perlegos
#
######################################################################

import os
import sys
import time
import pymongo

class CBmongo():
	def __init__(self):
		self.myhost = "ec2-54-234-14-163.compute-1.amazonaws.com"
		self.DCname = "dkan-cluster-1-dc-19"   #DC name for which you want to extract. Might have multiple clusters.
		print "***************"
		print "myhost = " + self.myhost
		print "***************"
		self.dbname = "vmware"
		self.statscollname = "stats_new"

	def testdb(self):
		self.getStats()
		print "*** Print all cluster names ***"
		clusters = self.getClusters('')
		print clusters
		print "***************"

		vmdata = {}  # vmdata sorted by clusterName: dict of dicts
		clusters = clusters[3:]      # select clusters you want
		for cl in clusters:  # get all VM data
			#print "* Getting data:", cl
			vmdata[cl] = self.getData(cl, 0, 10000)
		print "*** WAIT then print all VM data ***"
		time.sleep(5)
		for clp in vmdata.keys(): # print all VM data
			#print "*** NO PRINTING:", clp
			self.printData(vmdata[clp])

		print "***************"
		print "Done!"
		print "***************"

	def getStats(self):
		print "*** DB Stats ***"
		dbcon = pymongo.Connection(self.myhost)	        # opens connection to the DB
		dbpointer = dbcon[self.dbname]		        # DB pointer
		statresp = dbpointer.command({'dbstats': 1})
		#print statresp
		dbcon.close()  # Need to close DBconnection or it gets killed
		print "DB Storage Size in GBs:", float(statresp["storageSize"])/(1024*1024*1024)
		print "DB File Size in GBs:", float(statresp["fileSize"])/(1024*1024*1024)
		print "***************"

	def getClusters(self, DCname):
		dbcon = pymongo.Connection(self.myhost)	        # opens connection to the DB
		dbpointer = dbcon[self.dbname]		        # DB pointer
		clusters = dbpointer.vm.distinct('DCname')
		dbcon.close()  # Need to close DBconnection or it gets killed
		return clusters

	def getData(self, DCname, start=0, end=999999999999):
		# Returns dict with all data from given cluster sorted by VM
		#  DCname: cluster you want data from
		#  start: place in time to go back (0=now, 1000=back in time)
		#  end: number of data points you want
		vms = {}
		dbcon = pymongo.Connection(self.myhost)	        # opens connection to the DB
		dbpointer = dbcon[self.dbname]		        # DB pointer
		dbstatscoll = dbpointer[self.statscollname]	# selecting the relevant collection
		vmdb = dbpointer["vm"]
		print "*** Get VMs in DCcluster (" + DCname + ")"
		for vm in vmdb.find({"DCname" : DCname}):
			vms[vm["name"].strip()] = []			#storing all VMs ID into this dict

		numvms = len(vms)
		print "* # VMs in cluster:", numvms

		perfkeysdb = dbpointer["perfCounterIdMap"]
		perfkeys = {}
		for pk in perfkeysdb.find({"DCname": DCname}):
			perfkeys[pk["k"]] = pk["v"]    #storing (mapping) all performance metrics' keys with their name here
		
		print "* Extracting Data from DB: Takes time to transfer *"
		cnt = 0
		for c in dbstatscoll.find({"DCname":DCname}).sort([("time_current", -1)]).skip(start).limit(end):
			cnt += 1
			if cnt%200000 is 0:
				print cnt/200000   # Progress indicator
			r = c
			try:
				r["perfkey"] = perfkeys[c["key"]]
				vms[c["name"]].append(r)	    #storing the stats for vm in "vms" dict
			except:
				pass
		print "* COMPLETE: got data from DBcluster", DCname, "***"
		dbcon.close()  # Need to close DBconnection or it gets killed
		time.sleep(5)
		return vms

	def printData(self, vms):
		print "***************"
		print "*** Print VMs ***"   # Sorted by VM
		vmcount = 0   # VM counter
		for vm in vms:
			vmcount += 1    # vmcount increment for each VM
			stcount = 0    # timestamp counter
			t = []
			for st in vms[vm]:
				stcount += 1
				t.append(st["perfkey"] + ":" + str(st["value"]))
				tm = st["time_current"]
				t.append("time:" + str(tm) + ":")  # time is added after each data entry
			print "******"
			print vm, "::", ":".join(t)
			stcount = stcount / 2     # We collect cpu,mem. The stcount above is incrementing for each.
			print "*** data history count:", stcount
			print "VMcount: " , vmcount
			print "***************"

# TEST CODE
cbdb = CBmongo()  #init CBmongo
#cbdb.testdb()  # tests functions
print cbdb.getData("dkan-cluster-1-dc-19", 0,10000)

