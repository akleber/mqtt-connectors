#!/usr/bin/env python

"""Fetches some data from the go-eCharger local
json api and published them to mqtt every 5
seconds. 
Read-only."""

import paho.mqtt.client as paho  # pip install paho-mqtt
import requests
import time
import logging
import sys
from config import *


FREQUENCY = 5  # sleep in sec
EXCEPTION_DELAY = 120  # sleep in sec


def goecharger_data():

    values = {}

    try:
        url = "http://{}/status".format(GOECHARGER_HOST)
        r = requests.get(url, timeout=FREQUENCY - 0.5)
        r.raise_for_status()
        j = r.json()

        values['power_sum'] = (j['nrg'][7] + j['nrg'][8] + j['nrg'][9]) / 10
        values['cur_chg_e'] = int(j['dws']) / 360000  # Deka-Watt-Sec to kWh

    except requests.Timeout:
        logging.error(f"Requests: Timeout: {url}")
        time.sleep(EXCEPTION_DELAY)
    except requests.RequestException as e:
        logging.error(f"Requests: Exception: {e}")
        time.sleep(EXCEPTION_DELAY)

    return values


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    logging.getLogger("urllib3").setLevel(logging.INFO)

    mqttc = paho.Client('goecharger-mqtt-connector', clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set("{}/connectorstatus".format(GOECHARGER_MQTT_PREFIX), "go-eCharger Connector: LOST_CONNECTION", 0, retain=True)

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.publish("{}/connectorstatus".format(GOECHARGER_MQTT_PREFIX), "go-eCharger Connector: ON-LINE", retain=True)

    mqttc.loop_start()
    while True:
        try:
            values = goecharger_data()
            for k, v in values.items():
                (result, mid) = mqttc.publish("{}/{}".format(GOECHARGER_MQTT_PREFIX, k), str(v), 0)
                logging.debug("Pubish Result: {} MID: {} for {}: {}".format(result, mid, k, v))  # noqa E501                

            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.publish("{}/connectorstatus".format(GOECHARGER_MQTT_PREFIX), "go-eCharger Connector: OFF-LINE", retain=True)

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
