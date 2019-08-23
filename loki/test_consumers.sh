

#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./test_consumers.sh <yggdrasil_host>"
  exit
fi

echo '---------- survey_evalese ----------'
kafkacat -b $1:9092 -t survey_evalese -C -e
echo '------------------------------------'

echo '---------- survey_json ----------'
kafkacat -b $1:9092 -t survey_json -C -e
echo '---------------------------------'

echo '---------- survey_response ----------'
kafkacat -b $1:9092 -t survey_response -C -e
echo '-------------------------------------'

echo '---------- nlp_process ----------'
kafkacat -b $1:9092 -t nlp_process -C -e
echo '---------------------------------'

echo '---------- survey_metrics ----------'
kafkacat -b $1:9092 -t survey_metrics -C -e
echo '------------------------------------'
