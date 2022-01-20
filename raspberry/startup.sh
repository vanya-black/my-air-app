#!/usr/bin/bash
sudo cp /home/pi/my-air-app/raspberry/air_master.service /etc/systemd/system/air_master.service
sudo systemctl daemon-reload
sudo systemctl enable air_master.service
sudo systemctl restart air_master.service