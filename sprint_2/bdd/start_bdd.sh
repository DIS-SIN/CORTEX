#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: ./start_bdd.sh <backend_ip>"
  echo "Example: ./start_bdd.sh 10.0.1.23"
  exit
fi

cd data
tar xzvf surveys.tar.gz
cd ..

BACKEND_IP=$1

PATTERN=s/BACKEND_IP/$1/g
case "$(uname -s)" in
	Darwin)
		gsed $PATTERN behave/app.template.ini > behave/app.ini
		;;
	*)
		sed $PATTERN behave/app.ini > behave/app.ini
		;;
esac

docker-compose build
docker-compose run --rm behave

rm data/*.json
