#!/bin/bash

if [ $# -lt 2 ]; then
  echo "Usage: ./start_bdd.sh <backend_ip> <nlp_ip>"
  echo "Example: ./start_bdd.sh 10.0.1.23 10.0.1.119"
  exit
fi

cd data
tar xzvf surveys.tar.gz
cd ..

PATTERN=s/BACKEND_IP/$1/g
case "$(uname -s)" in
	Darwin)
		gsed $PATTERN behave/app.template.ini > behave/app.ini
		;;
	*)
		sed $PATTERN behave/app.template.ini > behave/app.ini
		;;
esac

PATTERN=s/NLP_IP/$2/g
case "$(uname -s)" in
	Darwin)
		gsed -i $PATTERN behave/app.ini
		;;
	*)
		sed -i $PATTERN behave/app.ini
		;;
esac

docker-compose build
docker-compose run --rm behave

rm data/*.json
