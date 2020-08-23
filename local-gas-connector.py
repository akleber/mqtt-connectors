#!/usr/bin/env python

import paho.mqtt.client as paho  # pip install paho-mqtt
import time
import logging
import sys
import pigpio

MQTT_PREFIX = 'gas'
BROKER_HOST = 'localhost'
BROKER_PORT = 1883
FREQUENCY_S = 1
GAS_GPIO = 27

m3abs = 0.0
gpio = None
reed_state_old = 1


def read_state():
    global m3abs

    with open('local-gas-connector.state') as f:
        m3abs = float(f.readline().strip())

    logging.info("Read initial value: {:.2f}".format(m3abs))


def init_gpio():
    global gpio
    gpio = pigpio.pi()
    gpio.set_mode(GAS_GPIO, pigpio.INPUT)
    gpio.set_pull_up_down(GAS_GPIO, pigpio.PUD_UP)

    logging.info('GPIO initialized')


def data():
    global reed_state_old
    global m3abs

    values = {}
    reed_state = gpio.read(GAS_GPIO)

    if reed_state == 1:
        logging.debug("Reed state open")
        reed_state_old = reed_state
    else:
        logging.debug("Reed state closed")

        if reed_state_old != reed_state:
            reed_state_old = reed_state

            m3abs += 0.01
            values['volume'] = "{:.2f}".format(m3abs)
            values['tick'] = '1'

            logging.debug("m3abs: {:.2f}".format(m3abs))

    return values


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    read_state()
    init_gpio()

    mqttc = paho.Client('local-gas-connector', clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set("{}/connectorstatus".format(MQTT_PREFIX), "Local Gas Connector: LOST_CONNECTION", 0, retain=True)

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.publish("{}/connectorstatus".format(MQTT_PREFIX), "Local Gas Connector: ON-LINE", retain=True)

    # initial value
    (result, mid) = mqttc.publish("{}/{}".format(MQTT_PREFIX, 'volume'), str("{:.2f}".format(m3abs)), 0, retain=True)
    logging.debug("Pubish Result: {} MID: {} for {}: {}".format(result, mid, k, v))  # noqa E501

    mqttc.loop_start()
    while True:
        try:
            values = data()
            for k, v in values.items():
                (result, mid) = mqttc.publish("{}/{}".format(MQTT_PREFIX, k), str(v), 0, retain=True)
                logging.debug("Pubish Result: {} MID: {} for {}: {}".format(result, mid, k, v))  # noqa E501                

            time.sleep(FREQUENCY_S)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.publish("{}/connectorstatus".format(MQTT_PREFIX), "Local Gas Connector: OFF-LINE", retain=True)

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
