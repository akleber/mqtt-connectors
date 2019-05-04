# fronius-mqtt-bridge

Python scripts
* to fetch data from various APIs like power flow realtime data from a fronius data manager and pubish it to a mqtt broker.
* for implementing controll-algorithms based on and setting via mqtt topics

I use it with [this setup](doc/setup.md).

# Requirements
* Tested with Python 3.5 on raspian

# Usage
Create, activate and setup venv:

```
cd fronius-mqtt-bridge
python3 -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt
```

Then set the right hostnames or ip addresss and ports in all python files that will be used and run for example:

```
python3 fronius-connector.py
```

The scripts will run in an infinite loop until an error happens or they are aborted via Ctrl+C.

# Acknowledgement
* [Jan-Piet Mens](https://jpmens.net/2013/03/10/visualizing-energy-consumption-with-mqtt/) for the inspiration for the script.
* Juraj's [battsett.jar](https://github.com/jandrassy/battsett)
* [InfluxDB Connector](https://thingsmatic.com/2017/03/02/influxdb-and-grafana-for-sensor-time-series/)

# ToDo

* One mainloop https://stackoverflow.com/a/49801719/5523503
* pubish only if a client is connected to the broker
* document my setup
* add connector for Zoe battery status
* improve battery-controller strategy
** take sunshine duration prognosis into accoount
* finish config.py
* extend goe-charger with controlling capabilities
* add goecharger-controller to set charging power based on available pv energy.
* allow charging if soc < 7%
* Status for battery-controller
* add Forecast for tomorrow
* connector for rpi temp sensor

