#!/bin/bash

kafkacat_path=`which kafkacat`

if [[ $kafkacat_path ]]; then
  echo "kafkacat already installed: $kafkacat_path"
  exit
fi

echo "Install kafkacat ..."

unameOut="$(uname -s)"
case "${unameOut}" in
  Linux*)
    sudo apt-get install kafkacat
    ;;
  Darwin*)
    brew install kafkacat
    ;;
  *)
    echo "Unsupported platform $unameOut"
    ;;
esac

echo 'Done.'
