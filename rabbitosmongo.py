# Moves data from RabbitMQ queue to mongoDB
#  Loads at server boot
#  Runs in background continuously
#  Pushes data to mongoDB for each msg RabbitMQ gets from data collector
#
# mongoDB is on 200GB volume in: /data/MongoDB
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
# to change this, kill the process: rabbitosmongo.py
# python rabbitosmongo.py
#
########################################################

import pika
from pymongo import Connection
import json
import time
import traceback
dbhost = 'datacollector.cloubrain.com'
rabbithost = 'datacollector.cloubrain.com'

dbconnection = Connection(dbhost,27017)
db = dbconnection['openstack']
collection = db['stats_new']

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbithost))
channel = connection.channel()
exchange = 'openstack'
queue_name= 'openstack'
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
        record = {}
        record["ip"] = ip
        record["DCname"] = dcname
        record["time_current"] = time.time()
        record["data"] = post
        collection.insert(record)
    except:
        print traceback.print_exc()
        pass
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name)
channel.start_consuming()
