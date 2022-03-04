#!/usr/bin/env python

"""Fetches diesel prices"""

import paho.mqtt.client as paho  # pip install paho-mqtt
import time
import logging
import sys
import requests
from pathlib import Path

from config import *
from secrets import *


FREQUENCY = 3600  # 1h
TIMEOUT = 10  #sec


def fetch_data():

    # 73ce263a-8b6a-4b3f-b283-a1f4dc0925c4 Aral Tankstelle Darmstädter Str.
    # 51d4b70c-a095-1aa0-e100-80009459e03a Supermarkt-Tankstelle WEITERSTADT IM ROEDLING 8 A
    # 213e33be-8b98-4a3f-8f52-fec1edbb6403 Shell Buettelborn A67 Buettelborn Sued

    values = {}

    tankstellen = ['73ce263a-8b6a-4b3f-b283-a1f4dc0925c4', '51d4b70c-a095-1aa0-e100-80009459e03a', '213e33be-8b98-4a3f-8f52-fec1edbb6403']

    try:
        tankstellenlist = ','.join(tankstellen)
        url = f"https://creativecommons.tankerkoenig.de/json/prices.php?ids={tankstellenlist}&apikey={TANKERKOENIG_API_KEY}"  # noqa E501
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()

        if not data['ok']:
            raise RuntimeError('tankerkoenig result not ok')

        values['aral'] = data['prices']['73ce263a-8b6a-4b3f-b283-a1f4dc0925c4']['diesel']
        values['metro'] = data['prices']['51d4b70c-a095-1aa0-e100-80009459e03a']['diesel']
        values['shell'] = data['prices']['213e33be-8b98-4a3f-8f52-fec1edbb6403']['diesel']

    except requests.exceptions.Timeout:
        logging.error(f"Timeout requesting {url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"requests exception {e}")

    return values


def update():
    values = fetch_data()
    for k, v in values.items():
        (result, mid) = mqttc.publish(f"{DIESEL_MQTT_PREFIX}/{k}", str(v), 0, retain=True) # noqa E501
        logging.info(f"Pubish Result: {result} MID: {mid} for {k}: {v}") # noqa E501


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    mqttc = paho.Client(f'{Path(__file__).stem}-connector', clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set(f"{DIESEL_MQTT_PREFIX}/connectorstatus", "Connector: LOST_CONNECTION", 0, retain=True) # noqa E501

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info(f"Connected to {BROKER_HOST}:{BROKER_PORT}")

    mqttc.publish(f"{DIESEL_MQTT_PREFIX}/connectorstatus", "Connector: ON-LINE", retain=True) # noqa E501

    mqttc.loop_start()
    while True:
        try:
            update()
            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.publish(f"{DIESEL_MQTT_PREFIX}/connectorstatus", "Connector: OFF-LINE", retain=True) # noqa E501

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info(f"Disconnected from to {BROKER_HOST}:{BROKER_PORT}")
