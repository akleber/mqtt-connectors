#!/usr/bin/env python

"""Fetches and sets the fronius battery charging
power in % via modbus.
Inspired by Juraj's battsett.jar."""

import paho.mqtt.client as paho  # pip install paho-mqtt
import time
import logging
import sys

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

MODBUS_HOST = 'fronius.fritz.box'
BATTERY_MQTT_PREFIX = 'battery'
BROKER_HOST = 'raspberrypi.fritz.box'
BROKER_PORT = 1883
FREQUENCY = 30


def battery_data():

    values = {}

    # Datentypen der Register "float32","uint64","uint16"
    #    'string': decoder.decode_string(8),
    #    'float': decoder.decode_32bit_float(),
    #    '16uint': decoder.decode_16bit_uint(),
    #    '8int': decoder.decode_8bit_int(),
    #    'bits': decoder.decode_bits(),

    client = ModbusClient(MODBUS_HOST, port=502)
    client.connect()

    r = client.read_holding_registers(40327 - 1, 2, unit=1)
    inWRte = BinaryPayloadDecoder.fromRegisters(r.registers, byteorder=Endian.Big) # noqa E501

    values['chg_p'] = inWRte.decode_16bit_uint() / 100
    print("batt_chg_p {}%".format(values['chg_p']))

    # client.write_register(40327-1,3000,unit=1)

    client.close()

    return values


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    mqttc = paho.Client('battery-mqtt-connector', clean_session=True)
    # mqttc.enable_logger()
    mqttc.will_set("{}/connectorstatus".format(BATTERY_MQTT_PREFIX), "LOST_CONNECTION", 0, retain=True) # noqa E501

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    mqttc.publish("{}/connectorstatus".format(BATTERY_MQTT_PREFIX), "ON-LINE", retain=True) # noqa E501

    mqttc.loop_start()
    while True:
        try:
            values = battery_data()
            for k, v in values.items():
                (result, mid) = mqttc.publish("{}/{}".format(BATTERY_MQTT_PREFIX, k), str(v), 0) # noqa E501
                logging.debug("Pubish Result: {} MID: {} for {}: {}".format(result, mid, k, v)) # noqa E501

            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            break
        except Exception:
            raise

    mqttc.publish("{}/connectorstatus".format(BATTERY_MQTT_PREFIX), "OFF-LINE", retain=True) # noqa E501

    mqttc.disconnect()
    mqttc.loop_stop()  # waits, until DISCONNECT message is sent out
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
