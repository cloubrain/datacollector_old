#!/usr/bin/python

import httplib
import json
import urllib

url = "172.16.23.131:5000"

user = "admin"
password = "tando1702"
usehttps = False

params = '{"auth":{"passwordCredentials":{"username": "admin", "password":"tando1702"}, "tenantId":"cee9fbd12b804d3d90f1bdc464eef3bb"}}'
headers = {"Content-Type": "application/json"}

# HTTP connection

if (usehttps == True):
  conn = httplib.HTTPSConnection(url, key_file='../cert/priv.pem', cert_file='../cert/srv_test.crt')
else:
  conn = httplib.HTTPConnection(url)

conn.request("POST", "/v2.0/tokens", params, headers)

# HTTP response
response = conn.getresponse()
data = response.read()
dd = json.loads(data)

conn.close()
apitoken = dd['access']['token']['id']

print "your token is: %s" % apitoken


# list servers
headers = {"X-Auth-Token": str(apitoken), "Content-type":"application/json"}

print headers
url = "172.16.23.131:8774"
# http://172.16.23.131:8774/v2/cee9fbd12b804d3d90f1bdc464eef3bb

conn = httplib.HTTPConnection(url)
conn.request("GET", "/v2/cee9fbd12b804d3d90f1bdc464eef3bb/servers", '{}', headers)

response = conn.getresponse()
data = response.read()
dd = json.loads(data)
print dd
serverId = str(dd['servers'][0]['id'])
print
print 
print serverId
print 
print


# list usage for instance
conn = httplib.HTTPConnection(url)
headers = {"X-Auth-Token": str(apitoken)} #, "Host":"identity.api.openstack.org", "Accept":"application/vnd.openstack.compute+json;version=2"}
conn.request("GET", "/v2/cee9fbd12b804d3d90f1bdc464eef3bb/servers/ad4acd21-fcf8-440e-838d-617c2c6dfec4/diagnostics", '{}', headers)
response = conn.getresponse()
data = response.read()
print data
