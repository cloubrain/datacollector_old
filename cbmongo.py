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
import pymongo, copy
import matplotlib.pyplot as plt

class CBmongo():
	def __init__(self):
		self.myhost = "ec2-54-234-14-163.compute-1.amazonaws.com"
		self.DCname = "dkan-cluster-1-dc-19"   #DC name for which you want to extract. Might have multiple clusters.
		print "***************"
		print "myhost = " + self.myhost
		print "***************"
		self.dbname = "vmware2"
		self.statscollname = "stats_new"

	def testdb(self):
		self.getStats()
		print "*** Print all cluster names ***"
		clusters = self.getClusters('')
		print clusters
		print "***************"

		vmdata = {}  # vmdata sorted by clusterName: dict of dicts
		#clusters = clusters[3:]      # select clusters you want
		for cl in clusters:  # get all VM data
			#print "* Getting data:", cl
			vmdata[cl] = self.getData(cl, 0, 100)
		print "*** WAIT then print all VM data ***"
		time.sleep(5)
		for clp in vmdata.keys(): # print all VM data
			print "*** NO PRINTING:", clp
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
		#  end: number of data points you want: (end-start)/#VMs = timeSteps/VM
		# Each time entry is a dict: perfMetrics returns a list of all the metrics
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
			perfMetrics = c["perfMetrics"]
			for x2 in perfMetrics:
				try:
				 	x2["perfkey"] = perfkeys[x2["k"]]
					try:
						del x["perfMetrics"]
					except:
						pass
				except:
					pass
                        vms[c["name"]].append(copy.deepcopy(c))
		print "* COMPLETE: got data from DBcluster", DCname, "***"
		dbcon.close()  # Need to close DBconnection or it gets killed
		return vms

	def printData(self, vms):   # Good example for pulling data from new getData
		print "***************"
		print "*** Print VMs ***"   # Sorted by VM
		vmcount = 0   # VM counter
		for vm in vms:
			vmcount += 1    # vmcount increment for each VM
			print vm
			stcount = 0    # timestamp counter
			for st in vms[vm]:
				stcount += 1
				tm = st["time_current"]
				perf = st["perfMetrics"]
				print "* time: " + str(tm) + " :: " + str(perf)
			print "******"
			print "* data history count:", stcount
			print "***************"
		print "VMcount: " , vmcount
		print "***************"

	def getcpu(self, dcname, ts):   # Get CPU data
		# dcname: cluster, ts: number of timesteps
		print "***************"
		print "*** Get CPU data ***"   # Sorted by VM
		vms = self.getData(dcname, 0, 21*ts)    # multiply ts by num VMs in cluster
		vmscpu = {}
		vmcount = 0   # VM counter
		for vm in vms:
			vmcount += 1    # vmcount increment for each VM
			stcount = 0    # timestamp counter
			cpudata = []
			for st in vms[vm]:
				stcount += 1
				tm = st["time_current"]
				perf = st["perfMetrics"]
				cpupk = perf[5]    # you can get any perf metric like this
				cpuv = cpupk['v']    # type is unicode
				cpuv = int(float(cpuv))
				while cpuv > 100:  # Scale down for now
					cpuv = cpuv / 5
				cpudata.append(cpuv)
			cpudata.reverse()
			vmscpu[vm] = cpudata
		print "VMcount: " , vmcount
		print "***************"
		return vmscpu

	def plotcpu(self, vms):
		# Takes a dict of VMs with list of 1 perfMetric
		print "* Plot Data into file: cpuplot.png"
		for vm in vms:
			data = vms[vm]
			plt.plot(data)
		plt.savefig("cpuplot.png")

	def plotcpus(self, vms):
		# Takes a dict of VMs with list of 1 perfMetric
		for vm in vms:
			plt.clf()
			vmdata = vms[vm]
			data = vmdata
			plt.plot(data)
			plt.savefig("plot_" + str(vm) + ".png")
		print "* Plot Data into files: plot_vmname.png"

	def plotPerf(self, dcname, ts):   # Get and plot perf 
		# dcname: cluster, ts: number of timesteps
		print "***************"
		print "*** Plot Data ***"   # Sorted by VM
		vms = self.getData(dcname, 0, 21*ts)    # multiply ts by num VMs in cluster
		#print vms
		for vm in vms:
			plt.clf()
			vmdata = vms[vm]
			data = []
			for st in vmdata:
				tm = st["time_current"]
				perf = st["perfMetrics"]
				for p in perf:  # Eventually resort by perfMetrics
					pv = int(float(p['v']))
				cpupk = perf[5]    # you can get any perf metric like this
				cpuv = cpupk['v']    # type is unicode
				cpuv = int(float(cpuv))
				data.append(cpuv)
			data.reverse()
			plt.plot(data)
			plt.savefig("plot_" + str(vm) + ".png")
		print "* Plot Data into files: plot_vmname.png"

	def plotPerfs(self, dcname, ts):   # Get and plot perfs
		# dcname: cluster, ts: number of timesteps
		print "***************"
		print "*** Plot all perfMetrics for 1 VM ***"   # Sorted by VM
		vms = self.getData(dcname, 0, 21*ts)    # multiply ts by num VMs in cluster
		vm = vms.popitem()
		vm = vms.popitem()  # Do this multiple times to get later VMs
		vm = vms.popitem()
		#vm = vms.popitem()
		#vm = vms.popitem()
		#vm = vms.popitem()
		vmdata = vm[1]
		i = 0
		while i < 16:
			plt.clf()
			data = []
			for st in vmdata:
				tm = st["time_current"]
				perf = st["perfMetrics"]
				cpupk = perf[i]    # you can get any perf metric like this
				cpuv = cpupk['v']    # type is unicode
				cpuv = int(float(cpuv))
				data.append(cpuv)
			data.reverse()
			plt.plot(data)
			plt.savefig("plot_" + str(i) + ".png")
			i += 1
		print "* Plot Data into files: plot_i.png"

# TEST CODE
cbdb = CBmongo()  #init CBmongo
#cbdb.testdb()  # tests functions
#cbdb.getStats()

#vms = cbdb.getData("dkan-cluster-1-dc-19", 0, 210)
#cbdb.printData(vms)

#vmscpu = cbdb.getcpu("dkan-cluster-1-dc-19", 40)
#cbdb.plotcpus(vmscpu)
cbdb.plotPerfs("dkan-cluster-1-dc-19", 50)

"""
for vm in vmscpu:
	print vm
	print vmscpu[vm]
while vmscpu:
	vm = vmscpu.popitem()
	print vm[1]
"""
