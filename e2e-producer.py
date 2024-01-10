import socket
import json
import time
import subprocess
import threading
import queue
from confluent_kafka import Producer

global bootstrapServer
global currentPing

# Configuration
region = "aws-us-east1-az1"
bootstrapServer="brokerhostname""
bootstrapPort=9092
saslUsername="usernamehere"
saslPassword="passwordhere"
topic = "latency_service"
# End Configuration

#Create Ping queue
currentPing = 0
ping = queue.LifoQueue()

seq = 0
bootstrapfinal="%s:%s" % (bootstrapServer, bootstrapPort)
conf = {'bootstrap.servers': bootstrapfinal,
        'security.protocol': "SASL_SSL",
        'sasl.mechanisms': "PLAIN",
        #'ssl.providers': "legacy",
        'sasl.username': saslUsername,
        'sasl.password': saslPassword,
        'client.id': socket.gethostname(),
        'queue.buffering.max.kbytes': 32000}

def pingChecker():
   while [ 1 ]:
      response = subprocess.run(['ping', '-c', '1', bootstrapServer], capture_output=True, text=True, check=True)
      result = response.stdout.split("/")
      ping.put(result[4])

def getPing():
   global currentPing
   if ping.empty() == False:
      currentPing = ping.get()
      ping.queue.clear()
   return currentPing

#Start Ping checker
threading.Thread(target=pingChecker, daemon=True).start()

#Connect to Kafka
p = Producer(conf)

while [ 1 ]:
   time.sleep(1)
   payload = {
              "region": region,
              "sequence": seq,
              "brokerPingRTT": getPing(),
              "produce_time": time.time()
             }
   p.produce(topic, key="", value=json.dumps(payload))
   p.flush()
   seq = seq + 1
