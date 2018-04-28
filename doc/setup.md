# Setup

To have faster access to the Fronius Realtime Date, without using solar.web and their app,
I have a [mosquitto](https://mosquitto.org) MQTT broker running on a Raspberry Pi and I am using
the [IoT OnOff](https://www.iot-onoff.com) app for visualizing its data.
On the Pi this script here runs in a loop to fetch data from the Fronius API an publish it to mosquitto every 2 seconds.

<img src="IoT_OnOff_Fronius.jpeg" height="300">

# Running as a service

On my raspian I use supervisord to run the connectors as a service with the following configuration file:

```
[program:fronius]
command=/home/pi/fronius-mqtt-bridge/venv/bin/python3 fronius-mqtt-bridge.py
directory=/home/pi/fronius-mqtt-bridge
autostart=true
autorestart=true
startretries=3
stderr_logfile=/var/log/supervisor/fronius.err.log
stdout_logfile=/var/log/supervisor/fronius.out.log
user=pi
```

To update supervisor.d with changes run

```
supervisorctl reread
supervisorctl update
```
