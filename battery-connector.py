#!/usr/bin/env python

"""Fetches and sets the fronius battery charging
power in % via modbus.
Inspired by Juraj's battsett.jar."""

import paho.mqtt.client as paho  # pip install paho-mqtt
import requests
import time
import logging
import sys

MODBUS_HOST = 'fronius.fritz.box'
BATTERY_MQTT_PREFIX = 'battery'
BROKER_HOST = 'raspberrypi.fritz.box'
BROKER_PORT = 1883
FREQUENCY = 10

def battery_data():

    values['chg_p'] = 100
    return values


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
   
    mqttc = paho.Client('battery-mqtt-connector', clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set("{}/connectorstatus".format(BATTERY_MQTT_PREFIX), "LOST_CONNECTION", 0, retain=True)

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.publish("{}/connectorstatus".format(BATTERY_MQTT_PREFIX), "ON-LINE", retain=True)

    mqttc.loop_start()
    while True:
        try:
            values = battery_data()
            for k, v in values.items():
                (result, mid) = mqttc.publish("{}/{}".format(BATTERY_MQTT_PREFIX, k), str(v), 0)
                logging.debug("Pubish Result: {} MID: {} for {}: {}".format(result, mid, k, v))  # noqa E501                

            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.publish("{}/connectorstatus".format(BATTERY_MQTT_PREFIX), "OFF-LINE", retain=True)

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
