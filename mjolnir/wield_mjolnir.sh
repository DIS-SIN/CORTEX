#!/bin/bash

if [ $# -lt 4 ]; then
  echo "Usage: ./wield_mjolnir.sh <option> <config_file> <source_directory> <target_directory> <extra_directories>"
  echo "Example:"
  echo "  ./wield_mjolnir.sh -metxsci ./tmp/cp.ini ./tmp"
  echo "Option:"
  echo "  -m: create target directory if none"
  echo "  -e: extract entities and relations into tsv files"
  echo "  -x: copy any *.tsv file from tsv sub-irectory of extra directories into target directory"
  echo "  -s: run schema file schema_for_jotunheimr.cql if jotunheimr is a local container"
  echo "  -c: configure sink connector"
  echo "  -i: local import data by producing messages to yggdrasil"
  echo "  -r: remote import data by producing messages to yggdrasil"
  exit
fi

res1=$(date +%s)

commands=$1
if [[ $commands == -* ]]; then
  shift
else
  commands=
fi

CFG_FILE=$1
SOURCE_DIR=$2
TARGET_DIR=$3
EXTR_DIRS=$4

if [[ $commands == *"m"* ]]; then
  if [[ ! -d $TARGET_DIR ]]; then
    echo "mkdir -p $TARGET_DIR"
    mkdir -p $TARGET_DIR
  fi
fi

if [[ $commands == *"e"* ]]; then
  echo "python extractor.py $CFG_FILE $SOURCE_DIR $TARGET_DIR"
  python extractor.py $CFG_FILE $SOURCE_DIR $TARGET_DIR
fi

if [[ $commands == *"x"* ]]; then
  if [[ $EXTR_DIRS == *":"* ]]; then
    E_DIRS=$(echo $EXTR_DIRS | tr ":" "\n")
    echo $E_DIRS
    for E_DIR in $E_DIRS
    do
      if [[ -d $E_DIR ]]; then
        echo "cp $E_DIR/tsv/*.tsv $TARGET_DIR/."
        cp $E_DIR/tsv/*.tsv $TARGET_DIR/.
      fi
    done
  else
    if [[ -d $EXTR_DIR ]]; then
      echo "cp $EXTR_DIR/tsv/*.tsv $TARGET_DIR/."
      cp $EXTR_DIR/tsv/*.tsv $TARGET_DIR/.
    fi
  fi
fi

if [[ $commands == *"s"* ]]; then
  BOLT_HOST_PORT=`python cfg_option.py $CFG_FILE jotunheimr credentials host`
  USER_NAME=`python cfg_option.py $CFG_FILE jotunheimr credentials username`
  PASSWORD=`python cfg_option.py $CFG_FILE jotunheimr credentials password`
  CONTAINER_NAME=`python cfg_option.py $CFG_FILE jotunheimr credentials container_name`

  echo 'Wait for Neo4j ...'
  end="$((SECONDS+300))"
  while true; do
    console_log=`echo "RETURN apoc.version();" | docker exec -i $CONTAINER_NAME /var/lib/neo4j/bin/cypher-shell -u $USER_NAME -p $PASSWORD -a bolt://$BOLT_HOST_PORT | grep 3 | head -n 1`
    [[ $console_log = *"3.5"*  ]] && break
    [[ "${SECONDS}" -ge "${end}" ]] && exit 1
    sleep 1
  done

  echo "(docker exec -i $CONTAINER_NAME /var/lib/neo4j/bin/cypher-shell -u $USER_NAME -p $PASSWORD -a bolt://$BOLT_HOST_PORT) < $TARGET_DIR/schema_for_jotunheimr.cql"
  (docker exec -i $CONTAINER_NAME /var/lib/neo4j/bin/cypher-shell -u $USER_NAME -p $PASSWORD -a bolt://$BOLT_HOST_PORT) < $TARGET_DIR/schema_for_jotunheimr.cql
  printf "Done.\n"
fi

if [[ $commands == *"c"* ]]; then
  CONNECT=`python cfg_option.py $CFG_FILE yggdrasil conf connect`
  printf "Creating sink connector ...\n"
  curl -X POST http://$CONNECT/connectors \
    -H 'Content-Type:application/json' \
    -H 'Accept:application/json' \
    -d @"$TARGET_DIR"/jotunheimr_sink.json
fi

if [[ $commands == *"i"* ]]; then
  printf "Producing messages ...\n"
  python producer.py $CFG_FILE $TARGET_DIR
  printf "Done.\n"
fi

if [[ $commands == *"r"* ]]; then
  printf "Producing messages ...\n"
  python producer.py $CFG_FILE $TARGET_DIR remote
  printf "Done.\n"
fi

res2=$(date +%s)
diff=`echo $((res2-res1)) | awk '{printf "%02dh:%02dm:%02ds\n",int($1/3600),int($1%3600/60),int($1%60)}'`
printf "\n[mjolnir] DONE. Total processing time: %s\n" $diff
