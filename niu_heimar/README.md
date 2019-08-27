# Docker sets for local deployment

Set of dockers that can be run on any computer for local development, testing, or stand-by subsystem.
- a complete set of dockers for `yggdrasil`: `zookeeper`, `broker`, `schema_registry`, `connect`, `control_center`, and `rest_proxy`
- a `jotunheimr` docker with `APOC, Graph Algorithms, GraphQL, and Streams`
libraries installed, plus `halin`

## Start `niu_heimar`:

    ./start_niu_heimar.sh <neo4j_dir> <public_ip>

  Use local ip:

    ./start_niu_heimar.sh ~/neo4j

  Use `public_ip`:

    ./start_niu_heimar.sh ~/neo4j cortex.da-an.ca

## Test `niu_heimar`:

From another computer (Ubuntu 18.04, Windows 10, Mac OS X):

`public_ip` is where the `niu_heimar` running

    ./test_yggdrasil.sh <public_ip>

for example:

    ./test_yggdrasil.sh 10.0.1.119
