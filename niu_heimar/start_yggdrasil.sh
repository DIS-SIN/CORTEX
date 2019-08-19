#!/bin/bash

PLUGINS=~/yggdrasil/connect/plugins/

if [[ ! -d "$PLUGINS" ]]; then
  mkdir -p $PLUGINS
fi

if [[ ! -d "$PLUGINS/neo4j-kafka-connect-neo4j-1.0.3" ]]; then
  sudo chmod -R 777 $PLUGINS
  curl --fail --silent --show-error --location --remote-name "https://github.com/neo4j-contrib/neo4j-streams/releases/download/3.5.3/neo4j-kafka-connect-neo4j-1.0.3.zip"
  sudo rm -rf $PLUGINS/neo4j-kafka-connect-neo4j-1.0.3
  unzip neo4j-kafka-connect-neo4j-1.0.3.zip -d $PLUGINS
  sudo chmod -R 777 $PLUGINS
  rm neo4j-kafka-connect-neo4j-1.0.3.zip
fi

unameOut="$(uname -s)"
case "${unameOut}" in
  Linux*)
    export LOCAL_IP=`hostname -I | cut -f 1 -d ' '`
    ;;
  Darwin*)
    export LOCAL_IP=`ipconfig getifaddr en0`
    ;;
esac



docker-compose -f yggdrasil.yml up -d --build

echo "Install kafkacat ..."
unameOut="$(uname -s)"
case "${unameOut}" in
  Linux*)
    sudo apt-get install kafkacat
    ;;
  Darwin*)
    brew install kafkacat
    ;;
  *)
    echo "kafkacat is not supported in Windows. Try other kafka clients."
    ;;
esac

echo "To access yggdrasil from outside of this machine, open following ports:"
echo "  2181 (zookeeper)"
echo "  8081 (schema_registry)"
echo "  8082 (rest_proxy)"
echo "  9021 (control_center)"
echo "  9092 (broker)"
