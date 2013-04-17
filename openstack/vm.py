#!/bin/python

################################################
url = "172.16.23.131:5000"
usehttps = False
user = 'admin'
password = 'tando1702'
tenantId = 'cee9fbd12b804d3d90f1bdc464eef3bb'
upload = False 
###############################################

import httplib
import json
import urllib
import datetime
import os
import sys
import json
import time
from pymongo import MongoClient
import matplotlib.pyplot as plt

class VMWare: 
  def __init__(self, name, uuid, info=None):
    self.name = name
    self.uuid = uuid
    self.info = info
    self.resources = {}


  def addData(self, info):
    for key in info['stats']:
      if not key in self.resources:
        self.resources[key] = []
      self.resources[key].append(int(info['stats'][key]))

  def importImage(self):
    for key in self.resources:
      print key, self.resources[key]
      plt.plot(self.resources[key])
      plt.savefig("./images/" +  self.name + "_" + key + ".png")
      plt.clf()

  def storeToDB(self):
    print self.name
    print self.uuid
    print self.info
    now = datetime.datetime.now()
    document = {"name": self.name, "uuid": self.uuid, "time": str(now), "stats": self.info}
    print document
    
    # connecto to mongodb 
    # TODO: check if we can't connect to mongodb or not
    # if yes, insert
    # if no, store to file
    try: 
      connection = MongoClient('localhost', 27017)
      db = connection['openstack']
      collection = db['vms']
      collection.insert(document)
    except Exception:
      # can not connect to local datbase
      # create folder based on the date 
      now = str(datetime.datetime.now()).split(' ')[0]
      directory = str(now)
      if not os.path.isdir("./" + directory + "/"):
        os.mkdir("./" + directory + "/")

      with open("./" + directory + "/" + "data.txt", "a") as myfile:
        myfile.write(json.dumps(document, separators=(',',':')) + "\n")
  
  def constructListOfResources(self):
    if 'time' in self.info:
      pass


class DataCollector:
  def __init__(self, user, password, url, tenantId, usehttps=False):
    #TODO: need to connect to Openstack API to get auth tokens 
    self.url = url
    self.user = user
    self.password = password
    self.tenantId = tenantId
    self.usehttps = usehttps
    self.tokens = None

    # keep track of all running servers 
    self.vms = []

    
  def sendRequest(self, url, method, path, params, headers, usehttps):
    if usehttps == True:
      conn = httplib.HTTPSConnection(url, key_file='../cert/priv.pem', cert_file='../cert/srv_test.crt')
    else:
      conn = httplib.HTTPConnection(url)
    # HTTP request
    conn.request(method, path, params, headers)

    # HTTP response
    response = conn.getresponse()
    data = response.read()
    dd = json.loads(data)
    return dd

  def listVM(self):
    #TODO: list all virtual machines (servers) running in OpenStack 
    pos = self.apiurl.find('/v2')
    url = self.apiurl[0:pos] # Ingore http:// at the beginning
    path = self.apiurl[pos:] + "/servers/detail"
    print url
    print path
    headers = {"X-Auth-Token": str(self.apitoken), "Content-type":"application/json"}
    method = 'GET'
    params = "{}"
    usehttps = self.usehttps

    response = self.sendRequest(url, method,path,  params, headers, usehttps)
    result = []
    for vm in response['servers']: 
      if vm['status'] == 'ACTIVE':
        result.append(vm)

    return result

  def getInfoVM(self, vm):
    method = 'GET'  
    pos = self.apiurl.find('/v2')
    url = self.apiurl[0:pos] # Ingore http:// at the beginning
    path = self.apiurl[pos:] + "/servers/" + vm['id'] + "/diagnostics"
    params = "{}"
    headers = {"X-Auth-Token": str(self.apitoken)} 
    usehttps = self.usehttps

    response = self.sendRequest(url, method, path, params, headers, usehttps)
    return response

  def storeToDatbase(self, vm):
    #TODO: get information about cpu usage, memory and other information about a virtual machine
    # store them to mongoDB or send to server
    pass

  def collect(self):
    #TODO: iterate all running server in OpenStack and store them to local database
    params = '{"auth":{"passwordCredentials":{"username": "%s", "password":"%s"}, "tenantId":"%s"}}' % (user, password, tenantId)
    headers = {"Content-Type": "application/json"}
    method = "POST"
    path = "/v2.0/tokens"

    response = self.sendRequest(url, method, path, params, headers, self.usehttps)
    self.apitoken = response['access']['token']['id']
    self.apiurl = response['access']['serviceCatalog'][0]['endpoints'][0]['publicURL'] # TODO: check with different version of OpenStack
    pos = self.apiurl.find("://")
    self.apiurl = self.apiurl[pos + 3:]

class Visualiztion: 
  def __init__(self):
    #TODO: connect to localhost or file 
    # collect data and import data
    try: 
      connection = MongoClient('localhost', 27017)
      db = connection['openstack']
      collection = db['vms']
      self.collection = collection
    except Exception:
      now = str(datetime.datetime.now()).split(' ')[0]
      directory = str(now)
      if not os.path.isdir("./" + directory + "/"):
        # there is nothing to visual for this date
        print "Can't make visualization"
      else: 
        self.fileData = open("./" + directory + "/data.txt", "r")
        self.collection = None

  def importImages(self):
    tableVMs = {}
    if self.collection != None:
      cursor = self.collection.find()
      while True:
        obj = next(cursor, None)
        if obj == None:
          break

        name = obj['name']
        uuid = obj['uuid']
        #TODO: create vms and add info to this vm
        if not uuid in tableVMs: 
          tableVMs[uuid] = VMWare(name, uuid)

        tableVMs[uuid].addData(obj)

      for vm in tableVMs: 
        tableVMs[vm].importImage()

    else: 
      for line in self.fileData.readlines():
        # TODO: replace single quote to double quote
        obj = json.loads(line)
        # load them and store to vms
        name = obj['name']
        uuid = obj['uuid']
        #TODO: create vms and add info to this vm
        if not uuid in tableVMs: 
          tableVMs[uuid] = VMWare(name, uuid)

        tableVMs[uuid].addData(obj)

      for vm in tableVMs: 
        tableVMs[vm].importImage()


# start the whole program here
if __name__ == '__main__':
  if len(sys.argv) == 2 and sys.argv[1] == 'visualization':
    visual = Visualiztion()
    visual.importImages()

    sys.exit()
  dc = DataCollector(user, password, url, tenantId, usehttps)
  while True: 
    dc.collect()
    for infoVM in dc.listVM():
      vm = VMWare(infoVM['name'], infoVM['id'], dc.getInfoVM(infoVM))
      vm.storeToDB()
    time.sleep(10)

