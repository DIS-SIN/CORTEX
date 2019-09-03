#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./run_draupnir.sh <yggdrasil_host>"
  echo "Example: ./run_draupnir.sh 10.0.1.119"
  exit
fi

export YGGDRASIL_HOST=$1

cd data
tar xzvf surveys.tar.gz
cd ..

python draupnir.py $YGGDRASIL_HOST

rm data/*.json
