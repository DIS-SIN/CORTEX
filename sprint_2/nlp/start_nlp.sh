#!/bin/bash

docker-compose up -d --build

echo "Make sure following ports are accesible from outside this host:"
echo "  9000 (stanfordnlp)"
