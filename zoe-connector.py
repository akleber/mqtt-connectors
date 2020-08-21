#!/usr/bin/env python

import paho.mqtt.client as paho  # pip install paho-mqtt
import time
import logging
import sys
from pyze.api import Gigya, Kamereon, Vehicle

import secrets


ZOE_MQTT_PREFIX = 'zoe'
BROKER_HOST = 'localhost'
BROKER_PORT = 1883
FREQUENCY = 1200  # sec


def getSocRange(gigya):

    k = Kamereon(api_key=secrets.KAMEREON_API_KEY, gigya=gigya, country='DE')
    v = Vehicle(secrets.ZOE_VIN, k)

    b = v.battery_status()
    soc = b['batteryLevel']
    remaining_range = b['batteryAutonomy']

    logging.info("Zoe API: soc: {}%, range: {}km".format(soc, remaining_range))

    return soc, remaining_range


def update(gigya):
    soc, remaining_range = getSocRange(gigya)

    (result, mid) = mqttc.publish("{}/{}".format(ZOE_MQTT_PREFIX, 'soc'), str(soc), 0, retain=True)
    # logging.info("Pubish Result: {} MID: {} for {}: {}".format(result, mid, 'soc', soc))

    (result, mid) = mqttc.publish("{}/{}".format(ZOE_MQTT_PREFIX, 'range'), str(remaining_range), 0, retain=True)
    # logging.info("Pubish Result: {} MID: {} for {}: {}".format(result, mid, 'range', remaining_range))


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    mqttc = paho.Client('zoe-connector', clean_session=True)
    # mqttc.enable_logger()

    try:
        g = Gigya(api_key=secrets.GIGYA_API_KEY)
        g.login(secrets.ZOE_ZE_USERNAME, secrets.ZOE_ZE_PASSWORD)  # You should only need to do this once
        g.account_info()  # Retrieves and caches person ID
    except Exception:
        logging.exception("Exception during Gigya login, sleeping 30s")
        time.sleep(30)
        raise

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.loop_start()
    while True:
        try:
            update(g)
            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            logging.warning("Keyboard interruption")
            break
        except Exception:
            logging.exception("Exception occured in loop")
            raise

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
