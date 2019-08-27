#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./test_yggdrasil_avro.sh <public_ip> <topic>"
  exit
fi

PUBLIC_IP=$1
TOPIC=$2

python test_yggdrasil.py $PUBLIC_IP:9092 http://$PUBLIC_IP:8081 $TOPIC
