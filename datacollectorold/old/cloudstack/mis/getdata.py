#!/usr/bin/python

import CloudStack 
from datetime import datetime
import time

api = 'http://localhost:8080/client/api'
apikey = 'Lows_2Nt-pw2Qth9ZF2L3yiCCkbmnxbyMa5nLYR6eYY4zgNJYVpzLcXgV30jp4PyBDKr9EXMbwHkwFkgtqLgsQ'
secret = 'yhrGXm9psX3XqKSk7Dqr8i681X6isHNBhkb7T1SwgHVrKnShBtSgo-l3x39flPbaJ3n8Tdz-mNrD9om8UL42YQ'

cloudstack = CloudStack.Client(api, apikey, secret)

vms = cloudstack.listVirtualMachines()

data = open("data.txt", "w")
while True:
  currentTime =  "[" + str(datetime.now()) + "]"
  for vm in vms:
    data.write(currentTime + "[" + vm['name'] + "]\n")
    if vm['state'] == 'Running':
      for key in vm.keys():
        data.write(str(key) + " : " + str(vm[key]) + "\n")

  time.sleep(10)
