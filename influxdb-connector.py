#!/usr/bin/env python3
# https://thingsmatic.com/2017/03/02/influxdb-and-grafana-for-sensor-time-series/
import paho.mqtt.client as mqtt
import datetime
import time
from influxdb import InfluxDBClient

BROKER_HOST = 'rpi3.kleber'
BROKER_PORT = 1883
INFLUXDB_HOST = 'albus.kleber'


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("#")


def on_message(client, userdata, msg):
    # print("Received a message on topic: " + msg.topic)
    # Use utc as timestamp
    receiveTime = datetime.datetime.utcnow()
    message = msg.payload.decode("utf-8")
    isfloatValue = False
    try:
        # Convert the string to a float so that it is stored as a number and not a string in the database
        val = float(message)
        isfloatValue = True
    except Exception:
        # print("Could not convert " + message + " to a float value")
        isfloatValue = False

    if isfloatValue:
        # print(str(receiveTime) + ": " + msg.topic + " " + str(val))

        json_body = [
            {
                "measurement": msg.topic,
                "time": receiveTime,
                "fields": {
                    "value": val
                }
            }
        ]

        dbclient.write_points(json_body)
        # print("Finished writing to InfluxDB")


print("start")

# Set up a client for InfluxDB
dbclient = InfluxDBClient(INFLUXDB_HOST, 8086, 'mqtt', 'mqtt', 'mqtt')
print("dbclient created")

# Initialize the MQTT client that should connect to the Mosquitto broker
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
connOK = False
while(connOK is False):
    try:
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        connOK = True
    except Exception:
        connOK = False
    time.sleep(2)

print("mqtt connection established")

# Blocking loop to the Mosquitto broker
client.loop_forever()
