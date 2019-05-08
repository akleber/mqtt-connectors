#!/usr/bin/env python

import paho.mqtt.client as paho  # pip install paho-mqtt
import time
import logging
import sys

from zoe_api.python.shared.zeservices import ZEServices

import secrets

ZOE_MQTT_PREFIX = 'zoe'
BROKER_HOST = 'rpi3.fritz.box'
BROKER_PORT = 1883
FREQUENCY = 600  # sec


def getSocRange():
    zeServices = ZEServices(secrets.ZE_USERNAME, secrets.ZE_PASSWORD)

    # ZE Services vehicle status.
    zeServices_json = zeServices.apiCall('/api/vehicle/' + secrets.VIN + '/battery')

    soc = zeServices_json['charge_level']
    remaining_range = zeServices_json['remaining_range']
    logging.info("Zoe API: soc: {}%, range: {}km".format(soc, remaining_range))

    return soc, remaining_range


def update():
    soc, remaining_range = getSocRange()

    (result, mid) = mqttc.publish("{}/{}".format(ZOE_MQTT_PREFIX, 'soc'), str(soc), 0, retain=True)
    logging.info("Pubish Result: {} MID: {} for {}: {}".format(result, mid, 'soc', soc))

    (result, mid) = mqttc.publish("{}/{}".format(ZOE_MQTT_PREFIX, 'range'), str(remaining_range), 0, retain=True)
    logging.info("Pubish Result: {} MID: {} for {}: {}".format(result, mid, 'range', remaining_range))


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
