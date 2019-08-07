#!/bin/bash

DATA_DIR=$1

if [[ ! -d "$DATA_DIR"/conv ]]; then
  mkdir -p "$DATA_DIR"/conv
  ls -d "$DATA_DIR"/conv
fi

tar xzvf $DATA_DIR/pc_v2015.tar.gz --directory $DATA_DIR/conv pc_v2015/pccfNat_AUG15_fccpNat.txt
mv $DATA_DIR/conv/pc_v2015/pccfNat_AUG15_fccpNat.txt $DATA_DIR/conv/pccfNat_AUG15_fccpNat.txt
rm -rf $DATA_DIR/conv/pc_v2015

docker-compose up -d yggdrasil_zookeeper yggdrasil_broker yggdrasil_schema_registry yggdrasil_connect yggdrasil_control_center

docker-compose up -d jotunheimr

./wield_mjolnir.sh -mextsci $DATA_DIR/cp/cp.ini $DATA_DIR/cp $DATA_DIR/tmp $DATA_DIR/cp
