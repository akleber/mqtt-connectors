#!/usr/bin/env python

import paho.mqtt.client as paho # pip install paho-mqtt
import requests
import json
import time
import sys

FRONIUS_HOST = 'fronius.fritz.box'
BROKER_HOST = 'raspberrypi.fritz.box'
BROKER_PORT = 1883
FREQUENCY = 2

def fronius_data():
    p_pv = -0.1
    p_grid = -0.1
    p_akku = -0.1
    p_load = -0.1

    try:
        url = "http://{}/solar_api/v1/GetPowerFlowRealtimeData.fcgi".format(FRONIUS_HOST)
        r = requests.get(url, timeout=FREQUENCY-0.5)
        r.raise_for_status()
        powerflow_data = r.json()
        p_pv = powerflow_data['Body']['Data']['Site']['P_PV']
        p_grid = powerflow_data['Body']['Data']['Site']['P_Grid']
        p_akku = powerflow_data['Body']['Data']['Site']['P_Akku']
        p_load = -powerflow_data['Body']['Data']['Site']['P_Load']
    except requests.exceptions.Timeout:
        print("Timeout requesting {}".format(url))
    except requests.exceptions.RequestException as e:
        print("requests exception {}".format(e))

    return (p_pv, p_grid, p_akku, p_load)


if __name__ == '__main__':
    mqttc = paho.Client('fronius-mqtt-brifge', clean_session=True)
    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    mqttc.loop_start()

    while True:
        try:
            (p_pv, p_grid, p_akku, p_load) = fronius_data()
            (result, mid) = mqttc.publish('fronius/p_pv', str(p_pv), 0)
            #print("Pubish Result: {} MID: {} p_pv: {}".format(result, mid, p_pv))
            (result, mid) = mqttc.publish('fronius/p_grid', str(p_grid), 0)
            #print("Pubish Result: {} MID: {} p_grid: {}".format(result, mid, p_grid))
            (result, mid) = mqttc.publish('fronius/p_akku', str(p_akku), 0)
            #print("Pubish Result: {} MID: {} p_akku: {}".format(result, mid, p_akku))
            (result, mid) = mqttc.publish('fronius/p_load', str(p_load), 0)
            #print("Pubish Result: {} MID: {} p_load: {}".format(result, mid, p_load))
            #print("")
            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except:
            raise
    mqttc.loop_stop()
    mqttc.disconnect()