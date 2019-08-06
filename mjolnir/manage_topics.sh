#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./manage_topics.sh <yggdrasil_zookeeper> <COMMAND> <topic>"
  echo "  ./manage_topics.sh list"
  echo "  ./manage_topics.sh describe my-topic"
  echo "  ./manage_topics.sh create my-topic"
  echo "  ./manage_topics.sh delete my-topic"
  exit
fi

YGGDRASIL_ZOOKEEPER=$1
commands=$2
topic=$3

if [[ $commands == *"list"* ]]; then
  docker exec -it $YGGDRASIL_ZOOKEEPER kafka-topics \
    --zookeeper $YGGDRASIL_ZOOKEEPER:2181 \
    --list
elif [[ $commands == *"describe"* ]]; then
  if [ $# -lt 2 ]; then
    docker exec -it $YGGDRASIL_ZOOKEEPER kafka-topics \
      --zookeeper $YGGDRASIL_ZOOKEEPER:2181 \
      --describe
  else
    docker exec -it $YGGDRASIL_ZOOKEEPER kafka-topics \
      --zookeeper $YGGDRASIL_ZOOKEEPER:2181 \
      --describe --topic $topic
  fi
elif [[ $commands == *"create"* ]]; then
  docker exec -it $YGGDRASIL_ZOOKEEPER kafka-topics \
    --zookeeper $YGGDRASIL_ZOOKEEPER:2181 \
    --create --topic $topic
elif [[ $commands == *"delete"* ]]; then
  docker exec -it $YGGDRASIL_ZOOKEEPER kafka-topics \
    --zookeeper $YGGDRASIL_ZOOKEEPER:2181 \
    --delete --topic $topic
fi
