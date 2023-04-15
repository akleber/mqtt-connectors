#!/usr/bin/env python3
# https://thingsmatic.com/2017/03/02/influxdb-and-grafana-for-sensor-time-series/
import paho.mqtt.client as mqtt
import datetime
import time
import json
from influxdb import InfluxDBClient
from config import *


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("#")


def on_message(client, userdata, msg):
    topic = msg.topic
    # print("Received a message on topic: " + topic)
    # Use utc as timestamp
    receiveTime = datetime.datetime.utcnow()
    message = msg.payload.decode("utf-8")

    if "tele/" in topic:
        send_tasmota_data(topic, receiveTime, message)
    else:
        send_plain_data(topic, receiveTime, message)


def send_tasmota_data(topic, receiveTime, message):
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        return

    energy = data.get("ENERGY")
    if not energy:
        return
    
    points = []
    for k,v in energy.items():
        try:
            float_v = float(v)
        except Exception:
            continue

        point = {
                "measurement": f"{topic}/{k}",
                "time": receiveTime,
                "fields": {
                    "value": float_v
                }
            }
        points.append(point)

    dbclient.write_points(points)


def send_plain_data(topic, receiveTime, message):
    try:
        # Convert the string to a float so that it is stored as a number and not a string in the database
        val = float(message)
    except Exception:
        # print("Could not convert " + message + " to a float value")
        return

    # print(str(receiveTime) + ": " + topic + " " + str(val))

    points = [
        {
            "measurement": topic,
            "time": receiveTime,
            "fields": {
                "value": val
            }
        }
    ]

    dbclient.write_points(points)
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
