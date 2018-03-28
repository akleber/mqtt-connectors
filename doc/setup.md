# Setup

To have faster access to the Fronius Realtime Date, without using solar.web and their app,
I have a [mosquitto](https://mosquitto.org) MQTT broker running on a Raspberry Pi and I am using
the [IoT OnOff](https://www.iot-onoff.com) app for visualizing its data.
On the Pi this script here runs in a loop to fetch data from the Fronius API an publish it to mosquitto every 2 seconds.

![IoT OnOff Fronis](IoT_OnOff_Fronius.jpeg){:height="300px"}