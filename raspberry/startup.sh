#!/usr/bin/bash
pip install -r /home/pi/my-air-app/requirements.txt

sudo cp /home/pi/my-air-app/raspberry/air_master.service /etc/systemd/system/air_master.service
sudo cp /home/pi/my-air-app/raspberry/sync_to_s3.service /etc/systemd/system/sync_to_s3.service
sudo cp /home/pi/my-air-app/raspberry/sync_to_s3.timer /etc/systemd/system/sync_to_s3.timer
sudo systemctl daemon-reload
sudo systemctl enable air_master.service
sudo systemctl restart air_master.service
sudo systemctl enable sync_to_s3.timer
sudo systemctl restart sync_to_s3.timer