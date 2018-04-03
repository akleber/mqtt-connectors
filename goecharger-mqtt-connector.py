#!/usr/bin/env python

import paho.mqtt.client as paho  # pip install paho-mqtt
import requests
import time
import logging
import sys

GOECHARGER_HOST = 'go-echarger.fritz.box'
GOECHARGER_MQTT_PREFIX = 'goe'
BROKER_HOST = 'raspberrypi.fritz.box'
BROKER_PORT = 1883
FREQUENCY = 5


def goecharger_data():

    values = {}

    try:
        url = "http://{}/status".format(GOECHARGER_HOST)
        r = requests.get(url, timeout=FREQUENCY - 0.5)
        r.raise_for_status()
        j = r.json()
        
        values['power_sum'] = (j['nrg'][7] + j['nrg'][8] + j['nrg'][9]) * 10


    except requests.exceptions.Timeout:
        print("Timeout requesting {}".format(url))
    except requests.exceptions.RequestException as e:
        print("requests exception {}".format(e))

    return values


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)

    mqttc = paho.Client('goecharger-mqtt-connector', clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set("{}/connectorstatus".format(GOECHARGER_MQTT_PREFIX), "LOST_CONNECTION", 0, retain=True)

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.publish("{}/connectorstatus".format(GOECHARGER_MQTT_PREFIX), "ON-LINE", retain=True)

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

    mqttc.publish("{}/connectorstatus".format(GOECHARGER_MQTT_PREFIX), "OFF-LINE", retain=True)

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
