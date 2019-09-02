#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./test_yggdrasil_json.sh <yggdrasil_public_ip>"
  exit
fi

YGGDRASIL_PUBLIC_IP=$1
TOPIC=$2

kafkacat -b $YGGDRASIL_PUBLIC_IP:9092,$YGGDRASIL_PUBLIC_IP:9093 -t $TOPIC -K: -P <<EOF
  1:{"title":"Frá Gylfa konungi ok Gefjuni","content":"Gefjun dró frá Gylfa glöð djúpröðul óðla, svá at af rennirauknum rauk, Danmarkar auka. Báru öxn ok átta ennitungl, þars gengu fyrir vineyjar víðri valrauf, fjögur höfuð."}
  2:{"title":"Gylfi kom til Ásgarðs","content":"Á baki létu blíkja, barðir váru grjóti, Sváfnis salnæfrar seggir hyggjandi."}
EOF
kafkacat -b $YGGDRASIL_PUBLIC_IP:9092,$YGGDRASIL_PUBLIC_IP:9093 -t $TOPIC -C -e
