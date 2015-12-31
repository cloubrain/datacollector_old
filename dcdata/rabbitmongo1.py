#!/usr/bin/env python
# rabbitmongo.py
# Moves data from RabbitMQ queue to mongoDB
#  Loads at server boot
#  Runs in background continuously
#  Pushes data to mongoDB for each msg RabbitMQ gets from data collector
#
# mongoDB is on 100GB volume in: /data/MongoDB
# log is in: /data/mongodb.log
#
# ssh into the server:
#  ssh -i cbopen.pem ec2-user@host
# make sure to: chmod 400 *.pem
# DANGER: THIS SERVER IS LIVE
#  Request a new server to mess around
#
# RabbitMQ vizualization:
# http://host:15672/
# user: guest
# pass: guest
#
########################################################

import pika
from pymongo import Connection
import json
import time
import traceback
dbhost = 'ec2-54-234-14-163.compute-1.amazonaws.com'
rabbithost = 'ec2-54-234-14-163.compute-1.amazonaws.com'

dbconnection = Connection(dbhost,27017)
db = dbconnection['vmware']
collection = db['stats_new']

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbithost))
channel = connection.channel()
exchange = 'CLSTR_MOITORING_EXCHANGE'
queue_name= 'CLSTR_MOITORING'
#channel.exchange_declare(exchange=exchange, type='fanout')
channel.queue_bind(exchange=exchange, queue=queue_name)

print ' [*] Waiting for messages. To exit press CTRL+C'

def callback(ch, method, properties, body):
    post= json.loads(body)
    try:
	ip = ''	
	dcname = ''
	try:
		ip = post["ip"]
	except:
		print traceback.print_exc()
		pass
	try:
		dcname = post["DCname"]
	except:
		print traceback.print_exc()
		pass
	if "COUNTERS" in post:
		nm = post["name"]
		for perf in post["COUNTERS"]:
			record = {}
			record["time_current"] = time.time()
			n = ''
			for k in perf:
				record[k] = perf[k]
				n = perf["v"]
			record["DCname"] = dcname
			record["ip"] = ip
			record["_id"]  = n.replace(".", "") + dcname + ip.replace(".", "")
			db[nm].save(record)
    		ch.basic_ack(delivery_tag = method.delivery_tag)
		return
        for i in post["STATS"]:
                 try:
                        db["vm"].save({"_id":i["name"].replace(".", "") + dcname + ip.replace(".", ""), "name":i["name"], "ip":ip, "DCname":dcname})
                 except:
			print traceback.print_exc()
                        pass
                 for j in i['STATS']:
                        record = {"time_current": time.time(), "name": i['name'], "uuid" : i['uuid'], "key" : j['k'], "value" : j['v']}
			record["ip"] = ip
			record["DCname"] = dcname
                        collection.insert(record)
    except:
	print traceback.print_exc()
        pass
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name)
channel.start_consuming()
