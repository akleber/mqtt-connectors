#!/usr/bin/env python

import paho.mqtt.client as paho  # pip install paho-mqtt
import time
import logging
import sys

import board
import adafruit_dht

# install libgpiod2:
# sudo apt-get install libgpiod2

MQTT_PREFIX = 'rpi'
BROKER_HOST = 'rpi3.kleber'
BROKER_PORT = 1883
FREQUENCY_S = 300

dhtDevice = adafruit_dht.DHT22(board.D4)


def data(retry=True):

    values = {}

    try:
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity

        values['waschkueche/temp'] = temperature_c
        values['waschkueche/humidity'] = humidity

        logging.info("{:.1f} C, {}% ".format(temperature_c, humidity))

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read
        logging.info("DHT error: ".format(str(error)))

        if retry:
            logging.info("Retrying in 3 sec...")
            time.sleep(3)
            values = data(False)
        else:
            logging.info("Not retrying again")

    return values


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    mqttc = paho.Client('local-dht-connector', clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set("{}/connectorstatus".format(MQTT_PREFIX), "Local DHT Connector: LOST_CONNECTION", 0, retain=True)

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.publish("{}/connectorstatus".format(MQTT_PREFIX), "Local DHT Connector: ON-LINE", retain=True)

    mqttc.loop_start()
    while True:
        try:
            values = data()
            for k, v in values.items():
                (result, mid) = mqttc.publish("{}/{}".format(MQTT_PREFIX, k), str(v), 0)
                logging.debug("Pubish Result: {} MID: {} for {}: {}".format(result, mid, k, v))  # noqa E501                

            time.sleep(FREQUENCY_S)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.publish("{}/connectorstatus".format(MQTT_PREFIX), "Local DHT Connector: OFF-LINE", retain=True)

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
