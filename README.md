# fronius-mqtt-bridge

Python script to fetch power flow realtime data from a fronius data manager API and pubish it to a mqtt broker.

# Requirements
* Tested with Python 3.5

# Usage
Create, activate and setup venv:

```
cd fronius-mqtt-bridge
python3 -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt
```

Then set the right hostnames or ip addresss and ports in fronius-mqtt-bridge.py and run:

```
python3 fronius-mqtt-bridge.py
```

# Acknowledgement
* [Jan-Piet Mens](https://jpmens.net/2013/03/10/visualizing-energy-consumption-with-mqtt/) for the inspiration for the script.

# ToDo

* pubish only if a client is connected to the broker
* add last will
* document my setup