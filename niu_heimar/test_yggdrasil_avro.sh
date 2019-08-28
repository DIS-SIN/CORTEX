#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./test_yggdrasil_avro.sh <yggdrasil_public_ip> <topic>"
  exit
fi

YGGDRASIL_PUBLIC_IP=$1
TOPIC=$2

python test_yggdrasil.py $YGGDRASIL_PUBLIC_IP:9092,$YGGDRASIL_PUBLIC_IP:9093 http://$YGGDRASIL_PUBLIC_IP:8081 $TOPIC
