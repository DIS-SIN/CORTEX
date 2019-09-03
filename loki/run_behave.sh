#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./run_behave.sh <yggdrasil_rest_proxy_ip> <yggdrasil_broker_ip> <yggdrasil_schema_registry_ip> <jotunheimr_ip>"
  echo "Example: ./run_behave.sh 10.0.1.23 10.0.1.23 10.0.1.23 10.0.1.119"
  exit
fi

YGGDRASIL_REST_PROXY_IP=$1
YGGDRASIL_BROKER_IP=$2
YGGDRASIL_SCHEMA_REGISTRY_IP=$3
JOTUNHEIMR_IP=$4

cd data
tar xzvf surveys.tar.gz
cd ..

behave \
  -D yggdrasil_rest_proxy=$YGGDRASIL_REST_PROXY_IP:8082 \
  -D yggdrasil_broker=$YGGDRASIL_BROKER_IP:9092,$YGGDRASIL_BROKER_IP:9093 \
  -D yggdrasil_schema_registry=$YGGDRASIL_SCHEMA_REGISTRY_IP:8081 \
  -D jotunheimr=$JOTUNHEIMR_IP:7687

rm data/*.json
