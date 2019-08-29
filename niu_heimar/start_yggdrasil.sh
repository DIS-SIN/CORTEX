#!/bin/bash

echo "Usage: ./start_yggdrasil.sh <public_ip>"
echo ""
echo "Use local ip: ./start_yggdrasil.sh"
echo "Use public ip: ./start_yggdrasil.sh 10.0.1.119"
echo ""

if [ $# -eq 1 ]; then
  export YGGDRASIL_PUBLIC_IP=$1
  echo "Use public ip "$YGGDRASIL_PUBLIC_IP

else
  unameOut="$(uname -s)"
  case "${unameOut}" in
    Linux*)
      export YGGDRASIL_PUBLIC_IP=`ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/'`
      ;;
    Darwin*)
      export YGGDRASIL_PUBLIC_IP=`ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}'`
      ;;
    MINGW*)
      export YGGDRASIL_PUBLIC_IP=`ipconfig | grep "IPv4" -A2 | grep -Fv 192.168 | grep IPv4 | grep -o '[^ ]*$'`
      ;;
    *)
      echo "Unsupported platform $unameOut."
      exit
      ;;
  esac
  echo "Use local ip "$YGGDRASIL_PUBLIC_IP
fi

echo "yggdrasil_broker(s) will listen on "$YGGDRASIL_PUBLIC_IP"."

./install_neo4j_kafka_connect_plugin.sh

./install_kafkacat.sh

docker-compose -f yggdrasil.yml up -d --build

echo "Make sure following ports are accesible from outside this host:"
echo "kafka "
echo "  2181 (zookeeper)"
echo "  8081 (schema_registry)"
echo "  8082 (rest_proxy)"
echo "  8083 (connect)"
echo "  9021 (control_center)"
echo "  9092, 9003 (brokers)"
