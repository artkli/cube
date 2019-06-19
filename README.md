# Instalacja MQTT Mosquitto + ZigBee + CC2531 + Aqara cube = sterowanie TV

Film:

https://youtu.be/QkiwCO7urYQ



Po podłączeniu CC2531 zainstalować MQTT i ZigBee bridge, bazując na instrukcji ze stron: https://diyprojects.io/test-zigbee2mqtt-project-hack-xiaomo-aqara-smart-home-gateway-assembly-demo-nodered-3d-printed-case/, https://gadget-freakz.com/diy-zigbee-gateway/:

MQTT:

```sh
sudo apt-get install mosquitto
sudo apt-get install mosquitto-clients
sudo pip install paho-mqtt
```

ZigBee bridge:

```sh
sudo curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash - 
sudo apt-get install -y nodejs git make g++ gcc
node --version
npm --version
sudo git clone https://github.com/Koenkk/zigbee2mqtt.git /opt/zigbee2mqtt
sudo chown -R pi:pi /opt/zigbee2mqtt
cd /opt/zigbee2mqtt
npm install
vi /opt/zigbee2mqtt/data/configuration.yaml
```

uruchom jako serwis:

```sh
sudo vi /etc/systemd/system/zigbee2mqtt.service
``` 

```
    [Unit]
    Description=zigbee2mqtt
    After=network.target
    [Service]
    ExecStart=/usr/bin/npm start
    WorkingDirectory=/opt/zigbee2mqtt
    StandardOutput=inherit
    StandardError=inherit
    Restart=always
    User=pi
    [Install]
    WantedBy=multi-user.target
```

```sh
sudo systemctl enable zigbee2mqtt.service
sudo systemctl start zigbee2mqtt

sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

Testowanie:

```sh
mosquitto_sub -h localhost -t "#" -v
```

Po dodaniu urządzenia można zmienić konfigurację:

```sh
vi /opt/zigbee2mqtt/data/configuration.yaml
```

uruchom program w Pythonie bazujący na bibliotece paho.mqtt.client jako serwis:

```sh
sudo vi /lib/systemd/system/cube.service
```

```
    [Unit]
    Description=Aqara Magic Cube TV remote control Service
    After=multi-user.target
    [Service]
    Type=idle
    ExecStart=/usr/bin/python /home/pi/zigbee/cube.py
    [Install]
    WantedBy=multi-user.target
```

```sh
sudo chmod 644 /lib/systemd/system/cube.service
sudo systemctl enable cube.service
```
