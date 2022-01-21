#!/usr/bin/bash
pip install -r /home/pi/my-air-app/requirements.txt

echo $1 $2 $3 $4

export S3_HOST=$1
export S3_ACCESS_KEY=$2
export S3_SECRET_KEY=$3
export S3_BUCKET=$4

sudo cp /home/pi/my-air-app/raspberry/air_master.service /etc/systemd/system/air_master.service
sudo cp /home/pi/my-air-app/raspberry/sync_to_s3.service /etc/systemd/system/sync_to_s3.service
sudo cp /home/pi/my-air-app/raspberry/sync_to_s3.timer /etc/systemd/system/sync_to_s3.timer
sudo systemctl daemon-reload
sudo systemctl enable air_master.service
sudo systemctl restart air_master.service
sudo systemctl enable sync_to_s3.timer
sudo systemctl restart sync_to_s3.timer