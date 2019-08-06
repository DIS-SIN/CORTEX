#!/bin/bash

if [ $# -lt 2 ]; then
  echo "Usage: ./wield_mjolnir.sh <instructions> <target_directory>"
  echo "Example:"
  echo "  ./wield_mjolnir.sh ~/data/ca_post.ini ~/data/ca_post"
  exit
fi

res1=$(date +%s)

BOLT_HOST_PORT=localhost:7687
USER_NAME=neo4j
PASSWORD="##dis@da2019##"
CONTAINER_NAME=jotunheimr

printf "Creating schema ...\n"
(docker exec -i $JOTUNHEIMR /var/lib/neo4j/bin/cypher-shell -u $USER_NAME -p $PASSWORD -a bolt://$BOLT_HOST_PORT) < "$2"/conf/schema_for_jotunheimr.cql
printf "Done.\n"

printf "Creating sink connector ...\n"
curl -X POST http://yggdrasil_connect:8083/connectors \
  -H 'Content-Type:application/json' \
  -H 'Accept:application/json' \
  -d @"$2"/conf/jotunheimr_sink.json
printf "Done.\n"

printf "Producing messages ...\n"
python producer $1 "$2"/tsv
printf "Done.\n"

res2=$(date +%s)
diff=`echo $((res2-res1)) | awk '{printf "%02dh:%02dm:%02ds\n",int($1/3600),int($1%3600/60),int($1%60)}'`
printf "\n[mjolnir] DONE. Total processing time: %s" $diff
