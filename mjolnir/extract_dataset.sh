#!/bin/bash

if [ $# -lt 3 ]; then
  echo "Usage: ./extract_dataset.sh <instructions> <target_directory> <input_file> <extra_dir>"
  echo "Example:"
  echo "  ./extract_dataset.sh ~/data/ca_post.ini ~/data/ca_post ~/data/raw/pccfNat_AUG15_fccpNat.txt ~/data/raw/extra"
  exit
fi

str1=$(date +%s)

CFG_FILE=$1
DATA_DIR=$2
TSV_FILE=$3
EXTR_DIR=$4
TMP_FILE=$(basename $TSV_FILE).utf8

iconv -f ISO-8859-1 -t UTF-8 $TSV_FILE > $DATA_DIR/$TMP_FILE

if [[ ! -d "$DATA_DIR"/tsv ]]; then
  mkdir $DATA_DIR/tsv
fi
if [[ ! -d "$DATA_DIR"/conf ]]; then
  mkdir $DATA_DIR/conf
fi

python extractor.py $CFG_FILE $DATA_DIR/$TMP_FILE $DATA_DIR/tsv $DATA_DIR/conf

rm $DATA_DIR/$TMP_FILE

if [[ -d $EXTR_DIR ]]; then
  cp $EXTR_DIR/*.tsv $DATA_DIR/tsv
fi

str2=$(date +%s)
diff=`echo $((str2-str1)) | awk '{printf "%02dh:%02dm:%02ds\n",int($1/3600),int($1%3600/60),int($1%60)}'`
printf "[Extracting dataset] DONE. Total processing time: %s\n" $diff
