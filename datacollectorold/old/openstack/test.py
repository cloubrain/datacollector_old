from novaclient.v1_1 import client
import novaclient
USER = 'admin'
PASS = 'tando1702'
TENANT = 'cee9fbd12b804d3d90f1bdc464eef3bb'
AUTH_URL = 'http://172.16.23.131:5000/v2.0'

#nt = client.Client(USER, PASS, TENANT, AUTH_URL, 'compute')
#print nt.servers.list()
print dir(novaclient.v1_1.client)
