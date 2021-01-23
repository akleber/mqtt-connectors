#!/usr/bin/env python

import paho.mqtt.client as paho  # pip install paho-mqtt
import time
import logging
import sys
import subprocess
from pathlib import Path
from config import *


FREQUENCY = 5 # query ever x sec


def viessmann_data():
    values = {}

    commands = "getTempVListM1,getTempRL17A,getTempWWist,getPumpeStatusM1"

    # vclient -h localhost:3002 -c getPumpeStatusM1,getTempWWist -t vcontrold-connector.tmpl
    p = subprocess.run(["/usr/local/bin/vclient", "-h", "localhost:3002", "-c", commands, "-t", "/root/mqtt-connectors/vcontrold-connector.tmpl"], capture_output=True, text=True)

    for line in p.stdout.splitlines():
        key, value = line.split(":")
        if isinstance(value, float):
            if float(value) > 2.0:
                values[key] = value
        else:
            values[key] = value

    return values


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    mqttc = paho.Client('vcontrold-connector', clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set("{}/connectorstatus".format(VCONTROLD_MQTT_PREFIX), "vcontrold Connector: LOST_CONNECTION", 0, retain=True)

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.publish("{}/connectorstatus".format(VCONTROLD_MQTT_PREFIX), "vcontrold Connector: ON-LINE", retain=True)

    mqttc.loop_start()
    while True:
        try:
            values = viessmann_data()
            for k, v in values.items():
                (result, mid) = mqttc.publish("{}/{}".format(VCONTROLD_MQTT_PREFIX, k), str(v), 0)
                logging.debug("Pubish Result: {} MID: {} for {}: {}".format(result, mid, k, v))  # noqa E501

            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.publish("{}/connectorstatus".format(VCONTROLD_MQTT_PREFIX), "vcontrold Connector: OFF-LINE", retain=True)

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
