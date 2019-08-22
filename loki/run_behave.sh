#!/bin/bash

if [ $# -lt 2 ]; then
  echo "Usage: ./run_behave.sh <yggdrasil_host> <jotunheimr_host>"
  echo "Example: ./run_behave.sh 10.0.1.119 10.0.1.23"
  exit
fi

export YGGDRASIL_HOST=$1
export JOTUNHEIMR_HOST=$1

behave -D yggdrasil_rest_proxy=$YGGDRASIL_HOST:8082 -D yggdrasil_broker=$YGGDRASIL_HOST:9092 -D yggdrasil_schema_registry=$YGGDRASIL_HOST:8081 -D jotunheimr=$jotunheimr_host:7687
