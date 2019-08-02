#!/bin/bash

res1=$(date +%s)

export MSYS_NO_PATHCONV=1

# create these environment variables 
# BOLT_HOST_PORT: The address and the port for the bolt driver
# USER_NAME: database username
# PASSWORD: database password
# NAMSPACE: the kubernetes namespace where the pods live
# POD_NAME: The name of the pod
# DATA_PATH: The directory containing the data
# TAR_FILE_NAME: The filename of the data tar file
 
TAR_PATH=$DATA_PATH$TAR_FILE_NAME

if [ ! -f $TAR_PATH ]; then 
   echo $TAR_PATH + " does not exist "
   exit 3
else
    printf "Copying tar file to pod \n "
    kubectl cp $TAR_PATH $NAMESPACE/$POD_NAME:/var/lib/neo4j/import
    printf "File copied... extracting data \n"
    kubectl exec -i $POD_NAME -- tar xvzf /var/lib/neo4j/import/$TAR_FILE_NAME
    printf "Extraction complete \n"
fi 


printf "Creating initial schema ...\n"
(kubectl exec -i $POD_NAME -- /var/lib/neo4j/bin/cypher-shell -u $USER_NAME -p $PASSWORD ) < ../scripts/import_scripts/data_schema.cql
printf "Done.\n"

printf "Import data ...\n"
(kubectl exec -i $POD_NAME -- /var/lib/neo4j/bin/cypher-shell -u $USER_NAME -p $PASSWORD ) < ../scripts/import_scripts/tsv_import.cql
printf "Done.\n"

printf "Convert data ...\n"
(kubectl exec -i $POD_NAME -- /var/lib/neo4j/bin/cypher-shell -u $USER_NAME -p $PASSWORD ) < ../scripts/import_scripts/data_convert_simple.cql
printf "Done.\n"

printf "Normalize data ...\n"
(kubectl exec -i $POD_NAME -- /var/lib/neo4j/bin/cypher-shell -u $USER_NAME -p $PASSWORD ) < ../scripts/import_scripts/data_normalization.cql
printf "Done.\n"

printf "Snapshot report ...\n"
(kubectl exec -i $POD_NAME -- /var/lib/neo4j/bin/cypher-shell -u $USER_NAME -p $PASSWORD ) < ../scripts/import_scripts/graph_db_report.cql
printf "Done.\n"

res2=$(date +%s)
diff=`echo $((res2-res1)) | awk '{printf "%02dh:%02dm:%02ds\n",int($1/3600),int($1%3600/60),int($1%60)}'`
printf "\n[Data import] DONE. Total processing time: %s.\n" $diff

export MSYS_NO_PATHCONV=0
