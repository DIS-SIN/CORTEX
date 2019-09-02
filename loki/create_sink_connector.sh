#!/bin/bash

if [ $# -lt 2 ]; then
  echo "Usage: ./create_sink_connector.sh <yggdrasil_connect_ip> <jotunheimr_ip>"
  echo "Example: ./create_sink_connector.sh 10.0.1.23 10.0.1.119"
  exit
fi

YGGDRASIL_CONNECT_IP=$1
JOTUNHEIMR_IP=$2

python process_template.py $JOTUNHEIMR_IP

curl -X POST http://$YGGDRASIL_CONNECT_IP:8083/connectors \
  -H 'Content-Type:application/json' \
  -H 'Accept:application/json' \
  -d @sink.neo4j.survey.json

echo ''
echo 'Done.'
