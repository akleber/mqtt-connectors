#!/usr/bin/env python

"""Fetches some data from the fronius json api
and publishes the result to mqtt.
Read only."""

import paho.mqtt.client as paho  # pip install paho-mqtt
import requests
import time
import logging
import sys
import numbers
from config import *

FREQUENCY = 3


def fronius_data():

    values = {}

    try:
        fronius_url = "http://{}/solar_api/v1/GetPowerFlowRealtimeData.fcgi".format(
            FRONIUS_HOST
        )
        r = requests.get(fronius_url, timeout=FREQUENCY - 0.5)
        r.raise_for_status()
        fronius_data = r.json()

        growatt_data = {}
        try:
            growatt_url = "http://{}/status".format(GROWATT_HOST)
            r = requests.get(growatt_url, timeout=FREQUENCY - 0.5)
            r.raise_for_status()
            growatt_data = r.json()
        except Exception:
            pass
        growatt_p_pv = int(growatt_data.get("OutputPower", 0))
        # print(f"growatt_p_pv: {growatt_p_pv}")

        values["p_pv"] = fronius_data["Body"]["Data"]["Site"]["P_PV"]
        values["p_grid"] = fronius_data["Body"]["Data"]["Site"]["P_Grid"]  # - is out
        values["p_akku"] = fronius_data["Body"]["Data"]["Site"]["P_Akku"]  # + is out
        values["p_load_orig"] = -fronius_data["Body"]["Data"]["Site"]["P_Load"]
        values["soc"] = fronius_data["Body"]["Data"]["Inverters"]["1"].get("SOC")
        values["battery_mode"] = fronius_data["Body"]["Data"]["Inverters"]["1"].get(
            "Battery_Mode"
        )
        values["e_day"] = fronius_data["Body"]["Data"]["Inverters"]["1"]["E_Day"] / 1000

        # handling for null/None values
        for k, v in values.items():
            if k == "battery_mode":
                continue
            if isinstance(v, numbers.Number):
                values[k] = int(v)
            else:
                values[k] = 0

        # print(f"p_pv: {values['p_pv']}")
        # print(f"p_grid: {values['p_grid']}")
        # print(f"p_akku: {values['p_akku']}")
        # print(f"p_load_orig: {values['p_load_orig']}")

        # p_load as reported by fronius inverter is wrong, as fronius does not know about
        # the growatt generator. He sees it as load, thats why the load can become negative,
        # whenever growatt is producing more power than what is actually consumed.
        # Here we account/adjust for growatt by computing the load ourself.
        # p_grid is the value reported by the fronius smart meter
        my_load = values["p_grid"] + values["p_pv"] + growatt_p_pv + values["p_akku"]
        values["p_load"] = my_load

        # print(f"my_load2: {my_load}")
        # load_diff = my_load - values['p_load']
        # print(f"load_diff: {load_diff}")

    except requests.exceptions.Timeout:
        print("Timeout requesting {}".format(fronius_url))
    except requests.exceptions.RequestException as e:
        print("requests exception {}".format(e))

    return values


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)

    mqttc = paho.Client("fronius-connector", clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set(
        "{}/connectorstatus".format(FRONIUS_MQTT_PREFIX),
        "Fronius Connector: LOST_CONNECTION",
        0,
        retain=True,
    )

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.publish(
        "{}/connectorstatus".format(FRONIUS_MQTT_PREFIX),
        "Fronius Connector: ON-LINE",
        retain=True,
    )

    mqttc.loop_start()
    while True:
        try:
            values = fronius_data()
            for k, v in values.items():
                result, mid = mqttc.publish(
                    "{}/{}".format(FRONIUS_MQTT_PREFIX, k), str(v), 0
                )
                logging.debug(
                    "Pubish Result: {} MID: {} for {}: {}".format(result, mid, k, v)
                )  # noqa E501

            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.publish(
        "{}/connectorstatus".format(FRONIUS_MQTT_PREFIX),
        "Fronius Connector: OFF-LINE",
        retain=True,
    )

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
