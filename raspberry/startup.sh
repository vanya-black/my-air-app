#!/usr/bin/bash
git clone https://github.com/vanya-black/my-air-app.git
sudo cp /home/pi/my-air-app/raspberry/air_master.service /etc/systemd/system/air_master.service
sudo systemctl daemon-reload
sudo systemctl enable air_master.service
sudo systemctl restart air_master.service