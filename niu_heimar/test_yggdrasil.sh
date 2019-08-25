#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./test_yggdrasil.sh <yggdrasil_host>"
  exit
fi

YGGDRASIL_HOST=$1

unameOut="$(uname -s)"
case "${unameOut}" in
  Linux*|Darwin*)

kafkacat -b $1:9092 -t test_topic_json -K: -P <<EOF
  1:{"title":"Frá Gylfa konungi ok Gefjuni","content":"Gefjun dró frá Gylfa glöð djúpröðul óðla, svá at af rennirauknum rauk, Danmarkar auka. Báru öxn ok átta ennitungl, þars gengu fyrir vineyjar víðri valrauf, fjögur höfuð."}
  2:{"title":"Gylfi kom til Ásgarðs","content":"Á baki létu blíkja, barðir váru grjóti, Sváfnis salnæfrar seggir hyggjandi."}
EOF
kafkacat -b $1:9092 -t test_topic_json -C -e
python test_yggdrasil.py $1:9092 http://$1:8081 test_topic_avro
  ;;

  *)
    python test_yggdrasil.py $1:9092 http://$1:8081 test_topic_avro
    ;;
esac
