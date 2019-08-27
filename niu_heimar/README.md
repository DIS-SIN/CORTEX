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

  Open ports for access on the host where you are running `niu_heimar` (as well as on the cloud host if you use any)

```
Make sure following ports are accesible from outside this host
kafka
  2181 (zookeeper)
  8081 (schema_registry)
  8082 (rest_proxy)
  8083 (connect)
  9021 (control_center)
  9092, 9003, 9004 (brokers)
neo4j
  3000 (halin)
  7473 (https)
  7474 (http)
  7687 (bolt)
```

## Test `niu_heimar`:

From another computer (Ubuntu 18.04, Windows 10, Mac OS X):

`public_ip` is where the `niu_heimar` running

    ./test_yggdrasil.sh <public_ip>

for example:

    ./test_yggdrasil.sh 10.0.1.119
