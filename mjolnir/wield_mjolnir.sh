#!/bin/bash

if [ $# -lt 5 ]; then
  echo "Usage: ./wield_mjolnir.sh <instructions>"
  echo "Example:"
  echo "  ./wield_mjolnir.sh yggdrasil_schema_registry yggdrasil_broker:9093 import_ca_post ~/data/ca_post province"
  exit
fi

YGGDRASIL_SCHEMA_REGISTRY=$1
YGGDRASIL_BROKER=$2
TOPIC_PREFIX=$3
DATA_PATH=$4
ENTITY_NAME=$5
SCHEMA=$(cat $DATA_PATH/avro/$ENTITY_NAME.avsc)
AWK_FM=$(cat $DATA_PATH/awk/$ENTITY_NAME.awk)

res1=$(date +%s)

./manage_topics.sh yggdrasil_zookeeper create $1

echo $DATA_PATH/tsv/$ENTITY_NAME.tsv
echo $AWK_FM

cat $DATA_PATH/tsv/$ENTITY_NAME.tsv | \
  awk -F'\t' "$AWK_FM" | \
  docker exec \
    --interactive $YGGDRASIL_SCHEMA_REGISTRY kafka-avro-console-producer \
    --broker-list $YGGDRASIL_BROKER \
    --topic $TOPIC_PREFIX'_'$ENTITY_NAME \
    --property value.schema="$SCHEMA"

res2=$(date +%s)
diff=`echo $((res2-res1)) | awk '{printf "%02dh:%02dm:%02ds\n",int($1/3600),int($1%3600/60),int($1%60)}'`
printf "\n[mjolnir] DONE. Total processing time: %s" $diff
