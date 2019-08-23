#!/bin/bash

HTTP_HOST_PORT=$1:7474
BOLT_HOST_PORT=$1:7687
USER_NAME=neo4j
PASSWORD="##dis@da2019##"
CONTAINER_NAME=jotunheimr

printf "Creating initial schema ...\n"
(docker exec -i $CONTAINER_NAME /var/lib/neo4j/bin/cypher-shell -u $USER_NAME -p $PASSWORD -a bolt://$BOLT_HOST_PORT) < jotunheimr_constraints.cql
printf "Done.\n"
