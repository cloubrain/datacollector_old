#!/usr/bin/python

from datetime import datetime
import os, sys, urllib2, urllib, time, base64, hashlib, re, hmac, getopt

################################################################################################
#                                 PLEASE HELP TO FILL OUT THIS                                 #
################################################################################################
api = 'http://localhost:8080/client/api'
apikey = 'DMzpNx7WGi3RG-vTMn7T218ZvEvN9wdHV4wjGqVFvj9pqSGqemC6ayRCLKr1Eq6d70snnxzCjuPKnzymXrUgCQ'
secret = 'Nbu5kKx6hSK_0JYEJw6XV9kwfepyuFJBqWV-ZTwOHiPFXFAkqF5ux86UICNTIkhqcaj_lVBaubZjslyzT4OHDw'
folder = '/var/log/datacollector'
SLEEP_TIME = 30
################################################################################################

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
  return response

def run():
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
    response = request('listVirtualMachines', {})
    fileData.write(str(datetime.now()) + " : " + response.read() + "\n")
    fileData.close()
    time.sleep(SLEEP_TIME)

def install(path):
  confFile = open("collect.conf", "w")
  confFile.write("description \"run collect.py as service\"\n")
  confFile.write("author \"Do Nguyen <ntd172@gmail.com>\"\n")

  confFile.write("start on runlevel [234]\n")
  confFile.write("stop on runlevel [0156]\n")

  output = os.popen("pwd")
  # need to read the whole line, but not last character "\n"
  path = output.readline()[:-1] + "/collect.py"
  output.close()
  print path
  confFile.write("exec python " + str(path) + " -r\n") 
  confFile.write("respawn\n")
  confFile.flush()
  confFile.close()



def usage():
  print "Usage: python collect.py [OPTION]"
  print "Collecting data of virtualmachine from cloudstack"
  print
  print "Options"
  print "\t-r, --run\t\t\tcollect data with configurations in collect.py"
  print "\t-i, --install=PATH\t\tpath to file collect.py"
  print "\t-h, --help"

if __name__ == "__main__":
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'r:i:h', ['run', 'install=', 'help']) 
  except getopt.GetoptError:
    usage()
    sys.exit(2)

  if opts == None or len(opts) == 0:
    usage()
    sys.exit(2)

  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage()
      sys.exit(2)
    elif opt in ('-r', '--run'):
      print "running"
    elif opt in ('-i', '--install'):
      print "Installing"
      print "Path = ", arg
      install(arg)
    else:
      usage()
      sys.exit(2)





