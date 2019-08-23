#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./start_sink_connector.sh <yggdrasil_host>"
  echo "Example: ./start_sink_connector.sh 10.0.1.119"
  exit
fi

export YGGDRASIL_HOST=$1

./create_jotunheimr_constraints.sh $YGGDRASIL_HOST

python process_template.py

curl -X POST http://$YGGDRASIL_HOST:8083/connectors \
  -H 'Content-Type:application/json' \
  -H 'Accept:application/json' \
  -d @sink.avro.neo4j.json

echo ''
echo 'Done.'
