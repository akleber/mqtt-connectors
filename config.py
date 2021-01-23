#!/usr/bin/env python

BROKER_HOST = 'mosquitto.kleber'
BROKER_PORT = 1883

INFLUXDB_HOST = 'influxdb.kleber'

FRONIUS_HOST = 'fronius.kleber'
FRONIUS_MQTT_PREFIX = 'fronius'

MODBUS_HOST = 'fronius.kleber'
BATTERY_MQTT_PREFIX = 'battery'

PV_P_TOPIC = 'fronius/p_pv'
SET_CHG_PCT_TOPIC = 'battery/set/chg_pct'
CHG_PCT_TOPIC = 'battery/chg_pct'
AUTO_CHG_TOPIC = 'battery/auto_chg_pct'
SOC_TOPIC = 'fronius/soc'

GOECHARGER_HOST = 'go-echarger.kleber'
GOECHARGER_MQTT_PREFIX = 'goe'

NETATMO_MQTT_PREFIX = 'netatmo'

ZOE_MQTT_PREFIX = 'zoe'

HEATER_MQTT_PREFIX = 'heater'

VCONTROLD_MQTT_PREFIX = 'vcontrold'
