#!/usr/bin/env python

BROKER_HOST = 'rpi3.fritz.box'
BROKER_PORT = 1883

FRONIUS_HOST = 'fronius.fritz.box'
FRONIUS_MQTT_PREFIX = 'fronius'

MODBUS_HOST = 'fronius.fritz.box'
BATTERY_MQTT_PREFIX = 'battery'

PV_P_TOPIC = 'fronius/p_pv'
SET_CHG_PCT_TOPIC = 'battery/set/chg_pct'
CHG_PCT_TOPIC = 'battery/chg_pct'
AUTO_CHG_TOPIC = 'battery/auto_chg_pct'

GOECHARGER_HOST = 'go-echarger.fritz.box'
GOECHARGER_MQTT_PREFIX = 'goe'
