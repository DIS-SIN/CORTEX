#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./run_remote_import.sh <dataset_directory> <jotunheimr_ip> <yggdrasil_broker_ip> <yggdrasil_schema_registry_ip> <yggdrasil_connect_ip>"
  echo "Example:"
  echo "  ./run_remote_import.sh ../datasets "
fi

DATA_DIR=$1
JOTUNHEIMR_IP=$2
YGGDRASIL_BROKER_IP=$3
YGGDRASIL_SCHEMA_REGISTRY_IP=$4
YGGDRASIL_CONNECT_IP=$5

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

./wield_mjolnir.sh -mx $DATA_DIR/tmp/config.ini $DATA_DIR $DATA_DIR/tmp $DATA_DIR/cp:$DATA_DIR/gc

cp $DATA_DIR/config.template.ini $DATA_DIR/tmp/config.ini

PATTERN=s/JOTUNHEIMR_PUBLIC/jotunheimr:7687/g
sed -i $PATTERN $DATA_DIR/tmp/config.ini

PATTERN=s/JOTUNHEIMR_CONTAINER/jotunheimr/g
sed -i $PATTERN $DATA_DIR/tmp/config.ini

PATTERN=s/YGGDRASIL_BROKER/$YGGDRASIL_BROKER_IP:9092/g
sed -i $PATTERN $DATA_DIR/tmp/config.ini

PATTERN=s/YGGDRASIL_SCHEMA_REGISTRY/"http:\/\/$YGGDRASIL_SCHEMA_REGISTRY_IP:8081"/g
sed -i $PATTERN $DATA_DIR/tmp/config.ini

PATTERN=s/YGGDRASIL_CONNECT/$YGGDRASIL_CONNECT_IP:8083/g
sed -i $PATTERN $DATA_DIR/tmp/config.ini

./wield_mjolnir.sh -e $DATA_DIR/tmp/config.ini $DATA_DIR $DATA_DIR/tmp $DATA_DIR/cp:$DATA_DIR/gc

rm -rf $DATA_DIR/cp/tsv $DATA_DIR/cp/src $DATA_DIR/gc/tsv $DATA_DIR/gc/src

./wield_mjolnir.sh -s $DATA_DIR/tmp/config.ini $DATA_DIR $DATA_DIR/tmp

sleep 10
./wield_mjolnir.sh -c $DATA_DIR/tmp/config.ini $DATA_DIR $DATA_DIR/tmp

sleep 10
./wield_mjolnir.sh -r $DATA_DIR/tmp/config.ini $DATA_DIR $DATA_DIR/tmp

rm -rf $DATA_DIR/tmp
