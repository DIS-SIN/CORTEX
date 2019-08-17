#!/bin/bash

DATA_DIR=$1

if [[ ! -f $DATA_DIR/cp/pc_v2015.tar.gz ]]; then
  echo 'pc_v2015.tar.gz not found.'
  exit
else
  rm -rf $DATA_DIR/cp/tsv
  rm -rf $DATA_DIR/cp/src
  tar xzvf $DATA_DIR/cp/pc_v2015.tar.gz --directory $DATA_DIR/cp
fi

if [[ ! -f $DATA_DIR/gc/gc_v2019.tar.gz ]]; then
  echo 'gc_v2019.tar.gz not found.'
  exit
else
  rm -rf $DATA_DIR/gc/tsv
  rm -rf $DATA_DIR/gc/src
  tar xzvf $DATA_DIR/gc/gc_v2019.tar.gz --directory $DATA_DIR/gc
fi

./wield_mjolnir.sh -mex $DATA_DIR/config.ini $DATA_DIR $DATA_DIR/tmp $DATA_DIR/cp:$DATA_DIR/gc
./wield_mjolnir.sh -mx $DATA_DIR/config.ini $DATA_DIR $DATA_DIR/tmp $DATA_DIR/cp:$DATA_DIR/gc

rm -rf $DATA_DIR/cp/tsv $DATA_DIR/cp/src $DATA_DIR/gc/tsv $DATA_DIR/gc/src

docker-compose up -d yggdrasil_zookeeper yggdrasil_broker yggdrasil_schema_registry yggdrasil_connect yggdrasil_control_center
docker-compose up -d jotunheimr

./wield_mjolnir.sh -s $DATA_DIR/config.ini $DATA_DIR $DATA_DIR/tmp

# TBD: Check if uggdrasil_connect is ready
sleep 15
./wield_mjolnir.sh -c $DATA_DIR/config.ini $DATA_DIR $DATA_DIR/tmp

# TBD: Check if sink connector end-point is ready before import
sleep 15
./wield_mjolnir.sh -i $DATA_DIR/config.ini $DATA_DIR $DATA_DIR/tmp

rm -rf $DATA_DIR/tmp
