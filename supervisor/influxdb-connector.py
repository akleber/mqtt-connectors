[program:influxdb-connector]
command=/home/pi/mqtt-connectors/venv/bin/python3 influxdb-connector.py
directory=/home/pi/mqtt-connectors
autostart=true
autorestart=true
startretries=3
stderr_logfile=/var/log/supervisor/influxdb-connector.err.log
stdout_logfile=/var/log/supervisor/influxdb-connector.out.log
user=pi
