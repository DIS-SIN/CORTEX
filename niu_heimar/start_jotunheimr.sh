#!/bin/bash

export LOCAL_IP=$1

if [ $# -lt 2 ]; then
  echo "Usage: ./start_jotunheimr.sh <neo4j_dir> <yggdrasil_host>"
  echo "Example: ./start_jotunheimr.sh 10.0.1.119"
  exit
fi

NEO4J_DIR=$1
export NEO4J_GDB_DATA=$NEO4J_DIR/data
export NEO4J_GDB_IMPT=$NEO4J_DIR/import
export NEO4J_GDB_LOGS=$NEO4J_DIR/logs

export YGGDRASIL_HOST=$2

docker-compose -f jotunheimr.yml up -d --build

curl -X POST http://$YGGDRASIL_HOST:8083/connectors \
  -H 'Content-Type:application/json' \
  -H 'Accept:application/json' \
  -d @sink.avro.neo4j.json

echo "To access jotunheimr from outside of this machine, open following ports:"
echo "  7473 (HTTPS)"
echo "  7474 (HTTP)"
echo "  7687 (Bolt)"
