#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./test_yggdrasil.sh <yggdrasil_host>"
  exit
fi

YGGDRASIL_HOST=$1

python test_sent_msg.py $1:9092 http://$1:8081 nlp_result
