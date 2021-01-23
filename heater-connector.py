#!/usr/bin/env python

import paho.mqtt.client as paho  # pip install paho-mqtt
import time
import logging
import sys
import subprocess
from pathlib import Path
from config import *


FREQUENCY = 5 # query ever x sec


def sensor_data():
    values = {}

    devices_path = Path('/sys/bus/w1/devices')

    for device in devices_path.iterdir():
        if not device.is_dir() or device.name == 'w1_bus_master1':
            continue

        device_temperature_file = devices_path / device / 'temperature'

        temperture_string = device_temperature_file.read_text()
        temperature = float(temperture_string) / 1000

        values[device.name] = temperature

    return values


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    mqttc = paho.Client('heater-connector', clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set("{}/connectorstatus".format(HEATER_MQTT_PREFIX), "Heater Connector: LOST_CONNECTION", 0, retain=True)

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.publish("{}/connectorstatus".format(HEATER_MQTT_PREFIX), "Heater Connector: ON-LINE", retain=True)

    mqttc.loop_start()
    while True:
        try:
            values = sensor_data()
            for k, v in values.items():
                (result, mid) = mqttc.publish("{}/{}".format(HEATER_MQTT_PREFIX, k), str(v), 0)
                logging.debug("Pubish Result: {} MID: {} for {}: {}".format(result, mid, k, v))  # noqa E501

            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.publish("{}/connectorstatus".format(HEATER_MQTT_PREFIX), "Heater Connector: OFF-LINE", retain=True)

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
