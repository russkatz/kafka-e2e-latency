import socket
import json
import time
import subprocess
import threading
import queue
from datetime import datetime
from confluent_kafka import Producer,Consumer

global bootstrapServer
global currentPing

# Configurations
region="aws-east1-az1"
bootstrapServer="broker host"
bootstrapPort=9092
saslUsername="usernameHere"
saslPassword="PasswordHere"
topic = "latency_service"
reportTopic = "latency_reports"
# End Configurations

#Create Ping queue
currentPing = 0
ping = queue.LifoQueue()

bootstrapfinal="%s:%s" % (bootstrapServer, bootstrapPort)
pconf = {'bootstrap.servers': bootstrapfinal,
        'security.protocol': "SASL_SSL",
        'sasl.mechanisms': "PLAIN",
        #'ssl.providers': "legacy",
        'sasl.username': saslUsername,
        'sasl.password': saslPassword,
        'client.id': socket.gethostname(),
        'queue.buffering.max.kbytes': 32000}


cconf = {'bootstrap.servers': bootstrapfinal,
        'security.protocol': "SASL_SSL",
        'sasl.mechanisms': "PLAIN",
        'sasl.username': saslUsername,
        'sasl.password': saslPassword,
        'group.id': "latency-service",
        'auto.offset.reset': "latest",
        'enable.auto.commit': "false"}

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
p = Producer(pconf)
c = Consumer(cconf)
c.subscribe(["latency_service"])
try:
    while True:
        msg = c.poll(1.0)
        if msg is not None and msg.error() is None:
           m = json.loads(msg.value())
           latency = float(time.time()) - float(m["produce_time"])
           report = { 'endpoint1': m["region"],
                      'endpoint1Sequence': m["sequence"],
                      'endpoint2': region,
                      'latencyMS': latency*1000,
                      'brokerPingRTT': getPing(),
                      'producerBrokerPingRTT': m["brokerPingRTT"],
                      'reportCreated': str(datetime.now())
                     }
           p.produce(reportTopic, key="", value=json.dumps(report))
           p.flush()
           print(report)
except KeyboardInterrupt:
    pass
finally:
    c.close()
