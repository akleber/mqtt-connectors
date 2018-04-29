#!/usr/bin/env python

"""."""

import paho.mqtt.client as paho  # pip install paho-mqtt
import time
import logging
import sys

BROKER_HOST = 'raspberrypi.fritz.box'
BROKER_PORT = 1883
FREQUENCY = 60
PV_P_TOPIC = 'fronius/p_pv'
SET_CHG_P_TOPIC = 'battery/set/chg_p'
CHG_P_TOPIC = 'battery/chg_p'

chg_p = 0
pv_p = 0


def update_chg_p():

    new_chg_p = 30

    (result, mid) = mqttc.publish(SET_CHG_P_TOPIC, str(new_chg_p), 0) # noqa E501
    logging.debug("Pubish Result: {} MID: {} for {}: {}".format(result, mid, SET_CHG_P_TOPIC, new_chg_p)) # noqa E501


def on_message(mqttc, obj, msg):
    if msg.topic == CHG_P_TOPIC:
        chg_p = int(msg.payload)
       
    if msg.topic == PV_P_TOPIC:
        pv_p = int(msg.payload)
        
    logging.debug("{} {} {}".format(msg.topic, str(msg.qos), str(msg.payload))) # noqa E501


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    mqttc = paho.Client('battery-controller', clean_session=True)
    # mqttc.enable_logger()
    
    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))
    
    mqttc.on_message = on_message
    mqttc.subscribe(PV_P_TOPIC, 0)
    mqttc.subscribe(CHG_P_TOPIC, 0)

    mqttc.loop_start()
    while True:
        try:
            update_chg_p()
            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
