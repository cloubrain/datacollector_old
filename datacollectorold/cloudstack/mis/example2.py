#!/usr/bin/python

import CloudStack

api = 'http://localhost:8080/client/api'
apikey = 'Lows_2Nt-pw2Qth9ZF2L3yiCCkbmnxbyMa5nLYR6eYY4zgNJYVpzLcXgV30jp4PyBDKr9EXMbwHkwFkgtqLgsQ'
secret = 'yhrGXm9psX3XqKSk7Dqr8i681X6isHNBhkb7T1SwgHVrKnShBtSgo-l3x39flPbaJ3n8Tdz-mNrD9om8UL42YQ'

cloudstack = CloudStack.Client(api, apikey, secret)

job = cloudstack.deployVirtualMachine({
    'serviceofferingid': '2',
    'templateid':        '214',
    'zoneid':            '2'
})

print "VM being deployed. Job id = %s" % job['jobid']

print "All Jobs:"
jobs = cloudstack.listAsyncJobs({})
for job in jobs:
    print  "%s : %s, status = %s" % (job['jobid'], job['cmd'], job['jobstatus'])
