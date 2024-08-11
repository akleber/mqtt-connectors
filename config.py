#!/usr/bin/env python

BROKER_HOST = 'mosquitto.kleber.home.arpa'
BROKER_PORT = 1883

INFLUXDB_HOST = 'influxdb.kleber.home.arpa'

FRONIUS_HOST = 'fronius.kleber.home.arpa'
FRONIUS_MQTT_PREFIX = 'fronius'
ENERGYMETER_MQTT_PREFIX = 'energymeter'

MODBUS_HOST = 'fronius.kleber.home.arpa'
BATTERY_MQTT_PREFIX = 'battery'

PV_P_TOPIC = 'fronius/p_pv'
SET_CHG_PCT_TOPIC = 'battery/set/chg_pct'
CHG_PCT_TOPIC = 'battery/chg_pct'
AUTO_CHG_TOPIC = 'battery/auto_chg_pct'
SOC_TOPIC = 'fronius/soc'

GOECHARGER_HOST = 'go-echarger.kleber.home.arpa'
GOECHARGER_MQTT_PREFIX = 'goe'

NETATMO_MQTT_PREFIX = 'netatmo'

ZOE_MQTT_PREFIX = 'zoe'

HEATER_MQTT_PREFIX = 'heater'

VCONTROLD_MQTT_PREFIX = 'vcontrold'

DIESEL_MQTT_PREFIX = 'diesel'
