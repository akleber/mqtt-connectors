#!/usr/bin/env python

import paho.mqtt.client as paho  # pip install paho-mqtt
import pyatmo
import time
import logging
import sys

import secrets


NETATMO_MQTT_PREFIX = 'netatmo'
BROKER_HOST = 'rpi3.kleber'
BROKER_PORT = 1883
FREQUENCY = 10 * 60  # in seconds

sensors_to_use = ['Temperature', 'CO2', 'Humidity', 'Noise', 'Pressure',
                  'AbsolutePressure', 'battery_percent',
                  'Rain', 'sum_rain_24', 'sum_rain_1']


def get_values(authorization):

    values = {}

    try:
        weatherData = pyatmo.WeatherStationData(authorization)
        weatherDataMap = weatherData.lastData()

        for station in weatherDataMap:
            for sensor in weatherDataMap[station]:
                if sensor in sensors_to_use:
                    values["{}/{}".format(station, sensor)] = weatherDataMap[station][sensor]

    except Exception as e:
        print("exception {}".format(e))

    return values


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)

    mqttc = paho.Client('netatmo-mqtt-connector', clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set("{}/connectorstatus".format(NETATMO_MQTT_PREFIX),
                   "netatmo Connector: LOST_CONNECTION", 0, retain=True)

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.publish("{}/connectorstatus".format(NETATMO_MQTT_PREFIX), "netatmo Connector: ON-LINE", retain=True)

    mqttc.loop_start()

    authorization = pyatmo.ClientAuth(
        clientId=secrets.NETATMO_CLIENT_ID,
        clientSecret=secrets.NETATMO_CLIENT_SECRET,
        username=secrets.NETATMO_USERNAME,
        password=secrets.NETATMO_PASSWORD,
    )

    while True:
        try:
            values = get_values(authorization)
            for k, v in values.items():
                (result, mid) = mqttc.publish("{}/{}".format(NETATMO_MQTT_PREFIX, k), str(v), qos=0, retain=True)
                logging.debug("Pubish Result: {} MID: {} for {}: {}".format(result, mid, k, v))  # noqa E501                

            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.publish("{}/connectorstatus".format(NETATMO_MQTT_PREFIX), "netatmo Connector: OFF-LINE", retain=True)

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
