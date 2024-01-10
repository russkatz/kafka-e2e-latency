# Kafka End to End Latency Monitoring Framework

Simple python based framework for monitoring your end to end latencies on your Kafka deployments. Supports running producers and consumers from multiple locations to enable insights across all your networks and regions.

Each Producer will write a simple event to the cluster
```
region: the configured region where the producer is running
sequence: A incrementing sequence number if you need to correlate reports
brokerPingRTT: The current ping time to the cluster from the producer (RTT)
produce_time: The time that this event was created on the producer
```


Every Consumer will read the events from every producer and write a report back to the cluster (reportTopic configuration)
```
endpoint1: The region name of the producer that created the event
endpoint1Sequence: The producer sequence number for the event
endpoint2: The region name of the consumer that create the report
latencyMS: The total end to end latency from when the producer created the event until the consumer read the event
brokerPingRTT: The current ping time to the cluster from the consumer
producerBrokerPingRTT: The ping time to the cluster from the producer when the event was created
reportCreated: When this report was created
```

## Setup
* Edit the configuration section at the top of both the consumer and producer scripts
* Run one producer and one consumer in each network/region/datacenter/location
* Ensure everything is synced to the same time service for most accurate results.

## Known limitations
* This was written by me, so it's probably pretty bad
* Supports only one bootstrap server, and this is the server used for monitoring ping times as well
* No error handling
* I could combine this into a single script

