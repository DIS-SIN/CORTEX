#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./test_yggdrasil.sh <public_ip>"
  exit
fi

PUBLIC_IP=$1

unameOut="$(uname -s)"
case "${unameOut}" in
  Linux*|Darwin*)
    ./test_yggdrasil_json.sh $PUBLIC_IP test_topic_json
    ./test_yggdrasil_avro.sh $PUBLIC_IP test_topic_avro
  ;;
  *)
    ./test_yggdrasil_avro.sh $PUBLIC_IP test_topic_avro
    ;;
esac
