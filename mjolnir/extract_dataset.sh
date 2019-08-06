#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./extract_dataset.sh <instructions> <tsv_file> <target_directory>"
  echo "Example:"
  echo "  ./extract_dataset.sh
    ~/data/ca_post.ini
    ~/datasets/canada_post/pccfNat_AUG15_fccpNat/pccfNat_AUG15_fccpNat.tx
    ~/data/ca_post"
  exit
fi

str1=$(date +%s)

CFG_FILE=$1
TSV_FILE=$2
DATA_DIR=$3
TMP_FILE=$(basename $TSV_FILE).utf8

iconv -f ISO-8859-1 -t UTF-8 $TSV_FILE > $DATA_DIR/$TMP_FILE.utf8
python extractor.py $CFG_FILE $DATA_DIR/$TMP_FILE.utf8 $DATA_DIR
rm $DATA_DIR/$TMP_FILE.utf8

str2=$(date +%s)
diff=`echo $((str2-str1)) | awk '{printf "%02dh:%02dm:%02ds\n",int($1/3600),int($1%3600/60),int($1%60)}'`
printf "[Extracting dataset] DONE. Total processing time: %s\n" $diff
