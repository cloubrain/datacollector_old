#!/usr/bin/python

from datetime import datetime
import json
import os
import urllib2
import urllib
import time
import base64
import hashlib
import re
import hmac

api = 'http://localhost:8080/client/api'
apikey = 'lNNdyYTxPI10hTAO4HyMVSkXgHDSqWjFDh8kq6orjvCzeUlxrHnY7gDjUS3FbEd0hDd7D-I9D-GKKME-mrKJ0w'
secret = 'oTbleTZGtdutFsM4hT1nLAmLXcak_El2sC_vVG2ASNgTi8NHlDg_QGV4rdKaJi9MbOZxedo9z3PGBKpbV9KZvg' 
folder = 'datacollector-other'
SLEEP_TIME = 30
commands = ['name', 'cpunumber', 'cpuspeed', 'cpuused', 'networkkbsread', 'networkkbswrite']

def request(command, args):
  args['apikey']   = apikey
  args['command']  = command
  args['response'] = 'json'
  
  params=[]
  
  keys = sorted(args.keys())

  for k in keys:
      params.append(k + '=' + urllib.quote_plus(args[k]).replace("+", "%20"))
 
  query = '&'.join(params)

  signature = base64.b64encode(hmac.new(
      secret, 
      msg=query.lower(), 
      digestmod=hashlib.sha1
  ).digest())

  query += '&signature=' + urllib.quote_plus(signature)

  response = urllib2.urlopen(api + '?' + query)
  decoded = json.loads(response.read())

  propertyResponse = command.lower() + 'response'
  if not propertyResponse in decoded:
      if 'errorresponse' in decoded:
          raise RuntimeError("ERROR: " + decoded['errorresponse']['errortext'])
      else:
          raise RuntimeError("ERROR: Unable to parse the response")

  response = decoded[propertyResponse]
  result = re.compile(r"^list(\w+)s").match(command.lower())

  if not result is None:
      type = result.group(1)

      if type in response:
          return response[type]
      else:
          # sometimes, the 's' is kept, as in :
          # { "listasyncjobsresponse" : { "asyncjobs" : [ ... ] } }
          type += 's'
          if type in response:
              return response[type]

  return response

# TODO: 
# need to implement run in back ground and will write to file
# with corresponding with date-file
# 2012-10-10.txt
# need to run this article for implementation
# http://stackoverflow.com/questions/4705564/python-script-as-linux-service-daemon

# create the directory for store all files
if not os.path.isdir(folder):
    os.mkdir(folder)

while True:
# get the file name for storing
  fileName = str(datetime.today()).split(' ')[0]
  fileData = open(folder + "/" + fileName, 'a')
  response = request('listVirtualMachines', {})[0]
  if response['state'] == 'Running':
    line = str(datetime.now())
    for command in commands:
      line += " " + str(response[command])

  fileData.write(line + "\n")
  fileData.close()
  time.sleep(SLEEP_TIME)



