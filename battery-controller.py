#!/usr/bin/env python

"""."""

import paho.mqtt.client as paho  # pip install paho-mqtt
import time
import logging
import sys
import datetime

BROKER_HOST = 'raspberrypi.fritz.box'
BROKER_PORT = 1883
FREQUENCY = 60
MAX_CHG_P = 2500
MAX_AC_P = 2900
PV_P_TOPIC = 'fronius/p_pv'
SET_CHG_P_TOPIC = 'battery/set/chg_p'
CHG_PPRRCENT_TOPIC = 'battery/chg_p'
AUTO_CHG_TOPIC = 'battery/auto_chg_p'
SET_AUTO_CHG_TOPIC = 'battery/set_auto_chg_p'

chg_percent = 0
pv_p = 0
auto_chg_p = False


def update_chg_p():

    new_chg_percent = 100 #if in doubt, no limit
    
    now = datetime.datetime.now()
    today1600 = now.replace(hour=16, minute=0, second=0, microsecond=0)
    today1030 = now.replace(hour=10, minute=30, second=0, microsecond=0)
    if now > today1030 and now < today1600:
        new_chg_p = pv_p - MAX_AC_P
        new_chg_percent = int((100 * new_chg_p) / MAX_CHG_P)
        logging.debug("computed new_chg_percent: {}".format(new_chg_percent)) # noqa E501
        
        if new_chg_percent < 10:
            new_chg_percent = 10
        
        if new_chg_percent > 100:
            new_chg_percent = 100

    logging.debug("final new_chg_percent: {}".format(new_chg_percent)) # noqa E501

    if new_chg_percent != chg_percent:
        (result, mid) = mqttc.publish(SET_CHG_P_TOPIC, str(new_chg_percent), 0) # noqa E501
        logging.debug("Pubish Result: {} MID: {} for {}: {}".format(result, mid, SET_CHG_P_TOPIC, new_chg_percent)) # noqa E501


def on_message(mqttc, obj, msg):
    if msg.topic == CHG_PERCENT_TOPIC:
        chg_percent = int(msg.payload)
        logging.debug("got new chg_percent: {}".format(chg_percent)) # noqa E501
       
    if msg.topic == PV_P_TOPIC:
        pv_p = int(msg.payload)
        logging.debug("got new pv_p: {}".format(pv_p)) # noqa E501
        
    if msg.topic == SET_AUTO_CHG_TOPIC:
        if msg.payload == 'True':
            auto_chg_p = True
        else:
            auto_chg_p = False
            
        (result, mid) = mqttc.publish(AUTO_CHG_TOPIC, msg.payload, 0)
        logging.debug("Pubish Result: {} MID: {} for {}: {}".format(result, mid, AUTO_CHG_TOPIC, msg.payload))  # noqa E501


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    mqttc = paho.Client('battery-controller', clean_session=True)
    # mqttc.enable_logger()
    
    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))
    
    mqttc.on_message = on_message
    mqttc.subscribe(PV_P_TOPIC, 0)
    mqttc.subscribe(CHG_PERCENT_TOPIC, 0)

    mqttc.loop_start()
    while True:
        try:
            if auto_chg_p:
                update_chg_p()
            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
