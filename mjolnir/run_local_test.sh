#!/bin/bash

DATA_DIR=$1

if [[ ! -f $DATA_DIR/pc_v2015.tar.gz ]]; then
  echo 'pc_v2015.tar.gz not found.'
  exit
fi

tar xzvf $DATA_DIR/pc_v2015.tar.gz --directory $DATA_DIR

./wield_mjolnir.sh -mex $DATA_DIR/cp.ini $DATA_DIR $DATA_DIR/tmp $DATA_DIR

docker-compose up -d yggdrasil_zookeeper yggdrasil_broker yggdrasil_schema_registry yggdrasil_connect yggdrasil_control_center
docker-compose up -d jotunheimr

./wield_mjolnir.sh -s $DATA_DIR/cp.ini $DATA_DIR $DATA_DIR/tmp $DATA_DIR

./wield_mjolnir.sh -c $DATA_DIR/cp.ini $DATA_DIR $DATA_DIR/tmp $DATA_DIR

# TBD: Check if sink connector end-point is ready before import
./wield_mjolnir.sh -i $DATA_DIR/cp.ini $DATA_DIR $DATA_DIR/tmp $DATA_DIR

rm -rf $DATA_DIR/tmp $DATA_DIR/pc_v2015.txt
