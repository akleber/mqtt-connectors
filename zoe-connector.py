#!/usr/bin/env python

import paho.mqtt.client as paho  # pip install paho-mqtt
import time
import logging
import sys

import secrets

ZOE_MQTT_PREFIX = 'zoe'
BROKER_HOST = 'rpi3.fritz.box'
BROKER_PORT = 1883
FREQUENCY = 600  # sec


def login():
    pass


def refresh():
    pass


def getToken():
    print(secrets.VIN)
    # login or refresh


def getSocRange():
    pass


def update():
    pass
    # (result, mid) = mqttc.publish("{}/{}".format(BATTERY_MQTT_PREFIX, k), str(v), 0, retain=True) # noqa E501
    # logging.info("Pubish Result: {} MID: {} for {}: {}".format(result, mid, k, v)) # noqa E501


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    mqttc = paho.Client('zoe-connector', clean_session=True)
    # mqttc.enable_logger()

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.loop_start()
    while True:
        try:
            update()
            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
