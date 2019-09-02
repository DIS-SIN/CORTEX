#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./test_sink_connector.sh <yggdrasil_public_ip> <jotunheimr_public_ip>"
  echo "Create connector and test: ./test_sink_connector.sh 10.0.1.119 10.0.1.120"
  echo "Test connector: ./test_sink_connector.sh 10.0.1.119"
  exit
fi

if [ $# -eq 2 ]; then
  JOTUNHEIMR_PUBLIC_IP=$2
  cp sink.avro.test.template.json sink.avro.test.json
  PATTERN=s/JOTUNHEIMR_PUBLIC_IP/$JOTUNHEIMR_PUBLIC_IP:7687/g
  case "$(uname -s)" in
  	Darwin)
  		gsed -i $PATTERN sink.avro.test.json
  		;;
  	*)
  		sed -i $PATTERN sink.avro.test.json
  		;;
  esac
fi

export YGGDRASIL_PUBLIC_IP=$1

if [ $# -eq 2 ]; then
  curl -X POST http://$YGGDRASIL_PUBLIC_IP:8083/connectors \
    -H 'Content-Type:application/json' \
    -H 'Accept:application/json' \
    -d @sink.avro.test.json
fi

python test_yggdrasil.py $YGGDRASIL_PUBLIC_IP:9092,$YGGDRASIL_PUBLIC_IP:9093 http://$YGGDRASIL_PUBLIC_IP:8081 test_avro
