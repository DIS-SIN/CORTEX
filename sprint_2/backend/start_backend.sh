#!/bin/bash

if [[ ! -d ~/neo4j ]]; then
  mkdir -p ~/neo4j/data
  mkdir -p ~/neo4j/logs
  mkdir -p ~/neo4j/import
fi

docker-compose up -d --build

echo "Make sure following ports are accesible from outside this host:"
echo "  3000 (halin)"
echo "  7473 (https)"
echo "  7474 (http)"
echo "  7687 (bolt)"
echo "  8088 (app)"
