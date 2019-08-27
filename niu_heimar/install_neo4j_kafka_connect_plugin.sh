#!/bin/bash

PLUGINS=~/yggdrasil/connect/plugins/

if [[ ! -d "$PLUGINS" ]]; then
  mkdir -p $PLUGINS
fi

if [[ ! -d "$PLUGINS/neo4j-kafka-connect-neo4j-1.0.3" ]]; then
  echo "Install neo4j-kafka-connect plugin ..."
  sudo chmod -R 777 $PLUGINS
  curl --fail --silent --show-error --location --remote-name "https://github.com/neo4j-contrib/neo4j-streams/releases/download/3.5.3/neo4j-kafka-connect-neo4j-1.0.3.zip"
  sudo rm -rf $PLUGINS/neo4j-kafka-connect-neo4j-1.0.3
  unzip neo4j-kafka-connect-neo4j-1.0.3.zip -d $PLUGINS
  sudo chmod -R 777 $PLUGINS
  rm neo4j-kafka-connect-neo4j-1.0.3.zip
  echo 'Done.'
else
  echo "neo4j-kafka-connect plugin already installed: $PLUGINS/neo4j-kafka-connect-neo4j-1.0.3"
fi
