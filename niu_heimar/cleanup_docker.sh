#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./cleanup_docker.sh <config> <rmi>"
  echo ""
  echo "Example: ./cleanup_docker.sh niu_heimar.yml"
  echo ""
  exit
fi

docker-compose -f $1 down
docker system prune -f
docker container rm -f $(docker container ls -aq)

commands=$2
if [[ $commands == *"rmi"* ]]; then
  docker image rm -f $(docker image ls -aq)
fi

docker system info
