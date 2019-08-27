#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./start_niu_heimar.sh <neo4j_dir> <public_ip>"
  echo ""
  echo "Use local ip: ./start_niu_heimar.sh ~/neo4j"
  echo "Use public ip: ./start_niu_heimar.sh ~/neo4j 10.0.1.119"
  echo ""
  exit
fi

NEO4J_DIR=$1
export NEO4J_GDB_DATA=$NEO4J_DIR/data
export NEO4J_GDB_IMPT=$NEO4J_DIR/import
export NEO4J_GDB_LOGS=$NEO4J_DIR/logs

if [ $# -eq 2 ]; then
  export PUBLIC_IP=$2

else
  unameOut="$(uname -s)"
  case "${unameOut}" in
    Linux*)
      export PUBLIC_IP=`ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/'`
      ;;
    Darwin*)
      export PUBLIC_IP=`ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}'`
      ;;
    MINGW*)
      export PUBLIC_IP=`ipconfig | grep "IPv4" -A2 | grep -Fv 192.168 | grep IPv4 | grep -o '[^ ]*$'`
      ;;
    *)
      echo "Unsupported platform $unameOut."
      exit
      ;;
  esac
fi

echo "yggdrasil_broker(s) will listen on $PUBLIC_IP."

./install_neo4j_kafka_connect_plugin.sh

./install_kafkacat.sh

docker-compose up -d --build

echo "Make sure following ports are accesible from outside this host:"
echo "kafka "
echo "  2181 (zookeeper)"
echo "  8081 (schema_registry)"
echo "  8082 (rest_proxy)"
echo "  8083 (connect)"
echo "  9021 (control_center)"
echo "  9092, 9003 (brokers)"
echo "neo4j "
echo "  3000 (halin)"
echo "  7473 (https)"
echo "  7474 (http)"
echo "  7687 (bolt)"
