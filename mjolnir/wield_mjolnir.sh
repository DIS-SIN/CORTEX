#!/bin/bash

if [ $# -lt 3 ]; then
  echo "Usage: ./wield_mjolnir.sh <option> <config_file> <source_directory> <target_directory> <extra_directory>"
  echo "Example:"
  echo "  ./wield_mjolnir.sh -tsc ./tmp/cp.ini ./tmp"
  echo "Option:"
  echo "  -m: create target directory if none"
  echo "  -e: convert any *.txt file in source directory to utf-8 encoding and store results in source's conv/ sub-directory"
  echo "  -x: copy any *.tsv file from extra directory into target directory"
  echo "  -t: extract entities and relations into tsv files"
  echo "  -s: run schema file schema_for_jotunheimr.cql if jotunheimr is a local container"
  echo "  -c: configure sink connector"
  echo "  -i: import data by producing messages to yggdrasil"
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
EXTR_DIR=$4

if [[ $commands == *"m"* ]]; then
  if [[ ! -d $TARGET_DIR ]]; then
    echo "mkdir -p $TARGET_DIR"
    mkdir -p $TARGET_DIR
    ls -d $TARGET_DIR
  fi
fi

if [[ $commands == *"e"* ]]; then
  for file in $SOURCE_DIR/conv/*.txt
  do
    echo "iconv -f ISO-8859-1 -t UTF-8 $file > $SOURCE_DIR/$(basename $file)"
    iconv -f ISO-8859-1 -t UTF-8 "$file" > "$SOURCE_DIR"/$(basename $file)
  done
  SOURCE_DIR=$SOURCE_DIR/conv
fi

if [[ $commands == *"t"* ]]; then
  echo "python extractor.py $CFG_FILE $SOURCE_DIR $TARGET_DIR"
  python extractor.py $CFG_FILE $SOURCE_DIR $TARGET_DIR
fi

if [[ $commands == *"x"* ]]; then
  if [[ -d $EXTR_DIR ]]; then
    echo "cp $EXTR_DIR/*.tsv $TARGET_DIR/."
    cp $EXTR_DIR/*.tsv $TARGET_DIR/.
  fi
fi

if [[ $commands == *"s"* ]]; then
  BOLT_HOST_PORT=`python cfg_option.py $CFG_FILE jotunheimr credentials direct_host`
  USER_NAME=`python cfg_option.py $CFG_FILE jotunheimr credentials username`
  PASSWORD=`python cfg_option.py $CFG_FILE jotunheimr credentials password`
  CONTAINER_NAME=`python cfg_option.py $CFG_FILE jotunheimr credentials container_name`

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

res2=$(date +%s)
diff=`echo $((res2-res1)) | awk '{printf "%02dh:%02dm:%02ds\n",int($1/3600),int($1%3600/60),int($1%60)}'`
printf "\n[mjolnir] DONE. Total processing time: %s\n" $diff
