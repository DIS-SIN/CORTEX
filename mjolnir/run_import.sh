#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./run_import.sh <dataset_directory>"
  echo "Example:"
  echo "  ./run_import.sh ../datasets "
fi

DATA_DIR=$1

# ./wield_mjolnir.sh -s $DATA_DIR/tmp/config.ini $DATA_DIR $DATA_DIR/tmp

./wield_mjolnir.sh -c $DATA_DIR/tmp/config.ini $DATA_DIR $DATA_DIR/tmp

sleep 10
./wield_mjolnir.sh -r $DATA_DIR/tmp/config.ini $DATA_DIR $DATA_DIR/tmp

rm -rf $DATA_DIR/tmp
