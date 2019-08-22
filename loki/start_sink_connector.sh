#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./start_sink_connector.sh <yggdrasil_host>"
  echo "Example: ./start_sink_connector.sh 10.0.1.119"
  exit
fi

export YGGDRASIL_HOST=$1

curl -X POST http://$YGGDRASIL_HOST:8083/connectors \
  -H 'Content-Type:application/json' \
  -H 'Accept:application/json' \
  -d @sink.avro.neo4j.json
