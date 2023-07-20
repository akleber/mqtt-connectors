#!/usr/bin/env python

"""Fetches some data from the fronius json api
and publishes the result to mqtt.
Read only.
Fronius meter via fronius api. It is very slow."""

import paho.mqtt.client as paho  # pip install paho-mqtt
import requests
import time
import logging
import sys
from config import *


FREQUENCY = 300  # 5min
TIMEOUT = 10  #sec


def energymeter_data():

    values = {}

    try:
        url = "http://{}/solar_api/v1/GetMeterRealtimeData.cgi?Scope=System".format(FRONIUS_HOST)  # noqa E501
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        meter_data = r.json()

        values['e_feedin'] = meter_data['Body']['Data']['0']['EnergyReal_WAC_Sum_Produced'] / 1000
        values['e_receive'] = meter_data['Body']['Data']['0']['EnergyReal_WAC_Sum_Consumed'] / 1000

        values['voltage_l1'] = meter_data['Body']['Data']['0']['Voltage_AC_Phase_1']
        values['voltage_l2'] = meter_data['Body']['Data']['0']['Voltage_AC_Phase_2']
        values['voltage_l3'] = meter_data['Body']['Data']['0']['Voltage_AC_Phase_3']

        # handling for null/None values
        for k, v in values.items():
            if v is None:
                values[k] = 0

    except requests.exceptions.Timeout:
        logging.exception("Timeout requesting {}".format(url))
    except requests.exceptions.RequestException as e:
        logging.exception("requests exception {}".format(e))

    return values


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)
    
    logging.getLogger("urllib3").setLevel(logging.INFO)

    mqttc = paho.Client('energymeter-connector', clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set("{}/connectorstatus".format(ENERGYMETER_MQTT_PREFIX), "Energymeter Connector: LOST_CONNECTION", 0, retain=True)

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.publish("{}/connectorstatus".format(ENERGYMETER_MQTT_PREFIX), "Energymeter Connector: ON-LINE", retain=True)

    mqttc.loop_start()
    while True:
        try:
            values = energymeter_data()
            for k, v in values.items():
                (result, mid) = mqttc.publish("{}/{}".format(ENERGYMETER_MQTT_PREFIX, k), str(v), 0)
                logging.debug("Pubish Result: {} MID: {} for {}: {}".format(result, mid, k, v))  # noqa E501                

            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.publish("{}/connectorstatus".format(ENERGYMETER_MQTT_PREFIX), "Energymeter Connector: OFF-LINE", retain=True)

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
