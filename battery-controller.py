#!/usr/bin/env python

"""."""

import paho.mqtt.client as paho  # pip install paho-mqtt
import time
import logging
import sys
import datetime
import math

BROKER_HOST = 'raspberrypi.fritz.box'
BROKER_PORT = 1883
FREQUENCY = 60
MAX_CHG_P = 2500
MAX_AC_P = 2900
PV_P_TOPIC = 'fronius/p_pv'
SET_CHG_P_TOPIC = 'battery/set/chg_pct'
CHG_PCT_TOPIC = 'battery/chg_pct'
AUTO_CHG_TOPIC = 'battery/auto_chg_pct'

chg_pct = 0
pv_p = 0
auto_chg_pct = False


def update_chg_p():

    new_chg_pct = 100  # if in doubt, no limit

    now = datetime.datetime.now()
    today1600 = now.replace(hour=16, minute=0, second=0, microsecond=0)
    today1030 = now.replace(hour=10, minute=30, second=0, microsecond=0)
    if now < today1030:
        new_chg_pct = 0

    if now >= today1030 and now < today1600:
        new_chg_p = pv_p - MAX_AC_P
        new_chg_pct = math.ceil((100 * new_chg_p) / MAX_CHG_P)
        # logging.debug("computed new_chg_pct: {}".format(new_chg_pct)) # noqa E501

        if new_chg_pct < 10:
            new_chg_pct = 10

        if new_chg_pct > 100:
            new_chg_pct = 100

    logging.info("final new_chg_pct: {}".format(new_chg_pct)) # noqa E501

    if new_chg_pct != chg_pct:
        (result, mid) = mqttc.publish(SET_CHG_P_TOPIC, str(new_chg_pct), 0, retain = True) # noqa E501
        logging.info("Pubish Result: {} for {}: {}".format(result, SET_CHG_P_TOPIC, new_chg_pct)) # noqa E501


def on_message(mqttc, obj, msg):
    if msg.topic == CHG_PCT_TOPIC:
        global chg_pct
        chg_pct = math.floor(float(msg.payload))
        logging.debug("got new chg_pct: {}".format(chg_pct)) # noqa E501

    if msg.topic == PV_P_TOPIC:
        global pv_p
        pv_p = math.floor(float(msg.payload))
        logging.debug("got new pv_p: {}".format(pv_p)) # noqa E501

    if msg.topic == AUTO_CHG_TOPIC:
        global auto_chg_pct
        if msg.payload == b'True':
            auto_chg_pct = True
        else:
            auto_chg_pct = False
        logging.info("got new auto_chg_pct: {}".format(auto_chg_pct)) # noqa E501


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)

    mqttc = paho.Client('battery-controller', clean_session=True)
    # mqttc.enable_logger()

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.on_message = on_message
    mqttc.subscribe(PV_P_TOPIC, 0)
    mqttc.subscribe(CHG_PCT_TOPIC, 0)
    mqttc.subscribe(AUTO_CHG_TOPIC, 0)

    mqttc.loop_start()
    while True:
        try:
            if auto_chg_pct:
                update_chg_p()
            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
