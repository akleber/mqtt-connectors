#!/usr/bin/env python

"""
Controlls the charging power of a fronius battery to achieve peak shaving.
My fronius symo hybrid 3-0.3 is capapble of 5kW input, but only
of 3kW AC output. My 4kWp Generator is sometimes able to generate more than
3kW and the fronius is in this case able to charge the battery with the power
above 3kW AC.
The fronius is not able to control how fast the battery is charged, but only
allows to set a time when charging should be started. But then the battery is
charged with full power.
My small battery however is then full in about 1.5h. So by limitting the
charging power I can achieve peak shaving for a longer time.
The control strategy below sets the charging power to the power exceeding 3kW.
With respect to a future goecharger-controller, this controller here only
handles the power above 3kW AC. The goecharger-controller handles everything
up to 3kW AC. So they both do not interfere.
"""

import paho.mqtt.client as paho  # pip install paho-mqtt
import time
import logging
import sys
import datetime
import math

BROKER_HOST = 'rpi3.kleber'
BROKER_PORT = 1883
FREQUENCY = 300
MAX_CHG_P = 2500
MAX_AC_P = 3000
PEAK_SHAVING_THRESHOLD = MAX_AC_P - (MAX_AC_P * 0.05)
PEAK_EASING_RESERVE = 25
MIN_CHARGE_PCT = 5
PV_P_TOPIC = 'fronius/p_pv'
SET_CHG_PCT_TOPIC = 'battery/set/chg_pct'
CHG_PCT_TOPIC = 'battery/chg_pct'
AUTO_CHG_TOPIC = 'battery/auto_chg_pct'
SOC_TOPIC = 'fronius/soc'

chg_pct = 0
pv_p = 0
auto_chg_pct = False
soc = 0


def publish_chg_pct(pct):
    if pct != chg_pct:
        (result, mid) = mqttc.publish(SET_CHG_PCT_TOPIC,
                                      str(pct), 0, retain=True)
        logging.debug("Pubish Result: {} for {}: {}".format(result,
                                                            SET_CHG_PCT_TOPIC,
                                                            pct))


def update_chg_p():

    now = datetime.datetime.now()
    noon = now.replace(hour=12, minute=00, second=0, microsecond=0)
    afternoon = now.replace(hour=15, minute=30, second=0, microsecond=0)

    # if soc < PEAK_EASING_RESERVE set charging to 100% to keep some
    # energy in the battery to support peak demands
    if soc < PEAK_EASING_RESERVE:
        publish_chg_pct(100)
        return

    # If we have enough enegery for peak demand easing but are not
    # yet (before noon) above the peak shaving threashold, do not charge
    # anymore, to keep reserve for peak shaving
    if soc >= PEAK_EASING_RESERVE and pv_p < PEAK_SHAVING_THRESHOLD and now < noon:
        publish_chg_pct(0)
        return

    # At noon adaptive charging (see below)
    # Prevent peak shaving as long as possible by not charging the battery
    # to quickly
    if pv_p >= PEAK_SHAVING_THRESHOLD:
        new_chg_p = pv_p - MAX_AC_P
        new_chg_pct = math.ceil((100 * new_chg_p) / MAX_CHG_P)

        # bring new_chg_pct between 10 and 100
        if new_chg_pct < MIN_CHARGE_PCT:
            new_chg_pct = MIN_CHARGE_PCT
        if new_chg_pct > 100:
            new_chg_pct = 100

        publish_chg_pct(new_chg_pct)
        return

    # before afternoon do not charge to fast
    if now < afternoon:
        publish_chg_pct(50)
        return

    # fail safe no limit
    # in the afternoon charge as fast/much as possibe
    publish_chg_pct(100)


def on_message(mqttc, obj, msg):
    if msg.topic == CHG_PCT_TOPIC:
        global chg_pct
        chg_pct = math.floor(float(msg.payload))
        logging.debug("got new chg_pct: {}".format(chg_pct))

    if msg.topic == PV_P_TOPIC:
        global pv_p
        pv_p = math.floor(float(msg.payload))
        logging.debug("got new pv_p: {}".format(pv_p))

    if msg.topic == AUTO_CHG_TOPIC:
        global auto_chg_pct
        if msg.payload == b'True':
            auto_chg_pct = True
            update_chg_p()
        else:
            auto_chg_pct = False
            # reset chg_pct to 100% when auto mode is disabled
            publish_chg_pct(100)

        logging.debug("got new auto_chg_pct: {}".format(auto_chg_pct))

    if msg.topic == SOC_TOPIC:
        global soc
        soc = int(msg.payload)
        logging.debug("got new soc: {}".format(soc))


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
    mqttc.subscribe(SOC_TOPIC, 0)

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
