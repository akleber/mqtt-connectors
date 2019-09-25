import paho.mqtt.client as paho  # pip install paho-mqtt
import requests
import logging
import sys
import time


FORECAST_API_DAY = 'https://api.forecast.solar/estimate/watthours/day/49.9/8.5/35/0/4.06'
FORECAST_MQTT_PREFIX = 'forecast'

BROKER_HOST = 'rpi3.kleber'
BROKER_PORT = 1883

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)

    url = FORECAST_API_DAY
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    j = r.json()

    today = time.strftime("%Y-%m-%d")
    forecast_today = j['result'][today]

    logging.info("Forecast today: {}".format(forecast_today))


    mqttc = paho.Client('forecastsolar-mqtt-connector', clean_session=True)
    # mqttc.enable_logger()

    mqttc.connect(BROKER_HOST, BROKER_PORT, 60)
    logging.info("Connected to {}:{}".format(BROKER_HOST, BROKER_PORT))

    k = 'day'
    v = forecast_today

    (result, mid) = mqttc.publish("{}/{}".format(FORECAST_MQTT_PREFIX, k), str(v), 0, retain=True)
    logging.info("Pubish Result: {} MID: {} for {}: {}".format(result, mid, k, v))  # noqa E501                

    mqttc.disconnect()
    logging.info("Disconnected from to {}:{}".format(BROKER_HOST, BROKER_PORT))
