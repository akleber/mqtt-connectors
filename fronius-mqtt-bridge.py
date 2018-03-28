#!/usr/bin/env python

import paho.mqtt.client as paho  # pip install paho-mqtt
import requests
import time
import logging
import sys

FRONIUS_HOST = 'fronius.fritz.box'
BROKER_HOST = 'raspberrypi.fritz.box'
BROKER_PORT = 1883
FREQUENCY = 2

def fronius_data():

    values = {}

    try:
        url = "http://{}/solar_api/v1/GetPowerFlowRealtimeData.fcgi".format(FRONIUS_HOST)  # noqa E501
        r = requests.get(url, timeout=FREQUENCY - 0.5)
        r.raise_for_status()
        powerflow_data = r.json()
        
        values['p_pv'] = powerflow_data['Body']['Data']['Site']['P_PV']
        values['p_grid'] = powerflow_data['Body']['Data']['Site']['P_Grid']
        values['p_akku'] = powerflow_data['Body']['Data']['Site']['P_Akku']
        values['p_load'] = -powerflow_data['Body']['Data']['Site']['P_Load']
        values['soc'] = powerflow_data['Body']['Data']['Inverters']['1']['SOC']

    except requests.exceptions.Timeout:
        print("Timeout requesting {}".format(url))
    except requests.exceptions.RequestException as e:
        print("requests exception {}".format(e))

    return values


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)

    mqttc = paho.Client('fronius-mqtt-bridge', clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set("fronius/bridgestatus", "LOST_CONNECTION", 0, retain=True)

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.publish("fronius/bridgestatus", "ON-LINE", retain=True)

    mqttc.loop_start()
    while True:
        try:
            values = fronius_data()
            for k, v in values.items():
                (result, mid) = mqttc.publish("fronius/{}".format(k), str(v), 0)
                logging.debug("Pubish Result: {} MID: {} for {}: {}".format(result, mid, k, v))  # noqa E501                

            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.publish("fronius/bridgestatus", "OFF-LINE", retain=True)

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
