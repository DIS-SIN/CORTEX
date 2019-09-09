#!/bin/bash

res1=$(date +%s)

echo 'Extract datasets into neo4j import directory ...'
docker-compose stop
sudo rm -f ~/neo4j/logs/import_report.log
sudo rm -rf ~/neo4j/data/databases
sudo rm ~/neo4j/import/*.tsv
tar xzvf datasets/datasets.tar.gz --directory ~/neo4j/import/
chmod 777 ~/neo4j/import/*.tsv
echo 'Done.'

HTTP_HOST_PORT=localhost:7474
BOLT_HOST_PORT=localhost:7687
USER_NAME=neo4j
PASSWORD="##dis@da2019##"
CONTAINER_NAME=jotunheimr

echo 'Prepare docker set ...'
docker-compose up -d --build
echo 'Done.'

echo 'Wait for Neo4j ...'
end="$((SECONDS+300))"
while true; do
  console_log=`(docker exec -i $CONTAINER_NAME /var/lib/neo4j/bin/cypher-shell -u $USER_NAME -p $PASSWORD -a bolt://$BOLT_HOST_PORT) < scripts/check_apoc.cql  | grep 3 | head -n 1`
  [[ $console_log = *"3.5"*  ]] && break
  [[ "${SECONDS}" -ge "${end}" ]] && exit 1
  sleep 1
done
echo 'Done.'

echo 'Import datasets ...'
docker exec -i $CONTAINER_NAME /var/lib/neo4j/bin/neo4j-admin import \
    --database=basic_datasets \
    --nodes:GC_ClsLvl /import/cl.tsv \
    --nodes:GC_JobCls /import/jc.tsv \
    --nodes:GC_OccGrp /import/oc.tsv \
    --nodes:GC_Org /import/org.tsv \
    --nodes:CP_Province /import/pr.tsv \
    --nodes:CP_PostCode /import/pc.tsv \
    --nodes:CP_CSD /import/csd.tsv \
    --nodes:CP_CSDType /import/csd_type.tsv \
    --nodes:CP_Community /import/cn.tsv \
    --nodes:CP_Location /import/lc.tsv \
    --relationships:CL_TO_JC /import/jc_TO_cl.tsv \
    --relationships:JC_TO_JC /import/jc_TO_jc.tsv \
    --relationships:JC_TO_OC /import/oc_TO_jc.tsv \
    --relationships:ORG_TO_ORG /import/org_TO_org.tsv \
    --relationships:CM_TO_CSD /import/cn_TO_csd.tsv \
    --relationships:CSD_TO_TYPE /import/csd_TO_csd_type.tsv \
    --relationships:CSD_TO_PR /import/csd_TO_pr.tsv \
    --relationships:CN_TO_PC /import/pc_TO_cn.tsv \
    --relationships:CN_TO_LC /import/lc_TO_cn.tsv \
    --relationships:PC_TO_LC /import/lc_TO_pc.tsv \
    --delimiter TAB --array-delimiter "|" --multiline-fields true \
    --report-file=/logs/import_report.log \
    --quote '"'
echo 'Done.'

if [[ -f "~/neo4j/logs/import_report.log" ]]; then
  printf "Import issues:\n"
  cat ~/neo4j/logs/import_report.log
fi

echo 'Moving database ...'
docker-compose stop
sudo rm -rf ~/neo4j/data/databases/graph.db
sudo mv ~/neo4j/data/databases/basic_datasets ~/neo4j/data/databases/graph.db
sudo chmod -R 777 ~/neo4j/data/databases
docker-compose up -d
echo 'Done.'

echo 'Wait for Neo4j ...'
end="$((SECONDS+300))"
while true; do
  console_log=`(docker exec -i $CONTAINER_NAME /var/lib/neo4j/bin/cypher-shell -u $USER_NAME -p $PASSWORD -a bolt://$BOLT_HOST_PORT) < scripts/check_apoc.cql  | grep 3 | head -n 1`
  [[ $console_log = *"3.5"*  ]] && break
  [[ "${SECONDS}" -ge "${end}" ]] && exit 1
  sleep 1
done
echo 'Done.'

printf "Creating initial schema ...\n"
(docker exec -i $CONTAINER_NAME /var/lib/neo4j/bin/cypher-shell -u $USER_NAME -p $PASSWORD -a bolt://$BOLT_HOST_PORT) < scripts/constraints.cql
printf "Done.\n"

printf "Snapshot report ...\n"
(docker exec -i $CONTAINER_NAME /var/lib/neo4j/bin/cypher-shell -u $USER_NAME -p $PASSWORD -a bolt://$BOLT_HOST_PORT) < scripts/graph_db_report.cql
printf "Done.\n"

res2=$(date +%s)
dt=$(echo "$res2 - $res1" | bc)
dd=$(echo "$dt/86400" | bc)
dt2=$(echo "$dt-86400*$dd" | bc)
dh=$(echo "$dt2/3600" | bc)
dt3=$(echo "$dt2-3600*$dh" | bc)
dm=$(echo "$dt3/60" | bc)
ds=$(echo "$dt3-60*$dm" | bc)

printf "\n[Data import] DONE. Total processing time: %d:%02d:%02d:%02d\n" $dd $dh $dm $ds
