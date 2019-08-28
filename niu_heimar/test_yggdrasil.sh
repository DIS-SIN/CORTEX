#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./test_yggdrasil.sh <yggdrasil_public_ip>"
  exit
fi

YGGDRASIL_PUBLIC_IP=$1

unameOut="$(uname -s)"
case "${unameOut}" in
  Linux*|Darwin*)
    ./test_yggdrasil_json.sh $YGGDRASIL_PUBLIC_IP test_topic_json
    ./test_yggdrasil_avro.sh $YGGDRASIL_PUBLIC_IP test_topic_avro
  ;;
  *)
    ./test_yggdrasil_avro.sh $YGGDRASIL_PUBLIC_IP test_topic_avro
    ;;
esac
