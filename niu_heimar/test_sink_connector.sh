#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./test_sink_connector.sh <yggdrasil_host> <c>"
  echo "Create connector and test: ./test_sink_connector.sh 10.0.1.119 c"
  echo "Test connector: ./test_sink_connector.sh 10.0.1.119"
  exit
fi

export PUBLIC_IP=$1

if [ $# -eq 2 ]; then
  curl -X POST http://$PUBLIC_IP:8083/connectors \
    -H 'Content-Type:application/json' \
    -H 'Accept:application/json' \
    -d @sink.avro.test.json
fi

python test_yggdrasil.py $PUBLIC_IP:9092 http://$PUBLIC_IP:8081 test_avro
