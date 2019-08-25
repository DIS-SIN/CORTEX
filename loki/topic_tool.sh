#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./topic_tool.sh <yggdrasil_zookeeper> <COMMAND> <topic>"
  echo "  ./topic_tool.sh yggdrasil_zookeeper list"
  echo "  ./topic_tool.sh yggdrasil_zookeeper describe my-topic"
  echo "  ./topic_tool.sh yggdrasil_zookeeper create my-topic"
  echo "  ./topic_tool.sh yggdrasil_zookeeper delete my-topic"
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
