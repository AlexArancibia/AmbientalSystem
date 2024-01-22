#!/bin/sh
echo “AmbientalPe Code Setup”
sudo cp ambiental.service /lib/systemd/system/
sudo chmod 664 /lib/systemd/system/ambiental.service
sudo chmod 777 /home/pi/Documents/main.py
sudo chmod 777 /home/pi/Documents/style.qss
sudo chmod 777 /home/pi/Documents/test.py
sudo pyrcc5 resorce.qrc -o resorce_rc.py
sudo systemctl daemon-reload
sudo systemctl enable ambiental.service
sudo reboot