#!/usr/bin/bash
echo "Start script started"
pip install -r /home/pi/my-air-app/requirements.txt

sudo cp /home/pi/my-air-app/raspberry/air_master.service /etc/systemd/system/air_master.service
sudo cp /home/pi/my-air-app/raspberry/sync_to_s3.service /etc/systemd/system/sync_to_s3.service
sudo cp /home/pi/my-air-app/raspberry/sync_to_s3.timer /etc/systemd/system/sync_to_s3.timer

sudo mkdir -p /etc/systemd/system/sync_to_s3.service.d
echo "[Service]" | sudo tee /etc/systemd/system/sync_to_s3.service.d/override.conf
echo "Environment=S3_Host=$1" | sudo tee -a /etc/systemd/system/sync_to_s3.service.d/override.conf
sudo echo "Environment=S3_ACCESS_KEY=$2" | sudo tee -a /etc/systemd/system/sync_to_s3.service.d/override.conf
sudo echo "Environment=S3_SECRET_KEY=$3" | sudo tee -a /etc/systemd/system/sync_to_s3.service.d/override.conf
sudo echo "Environment=S3_BUCKET=$4" | sudo tee -a /etc/systemd/system/sync_to_s3.service.d/override.conf

sudo systemctl daemon-reload
sudo systemctl enable air_master.service
sudo systemctl restart air_master.service
sudo systemctl enable sync_to_s3.timer
sudo systemctl restart sync_to_s3.timer