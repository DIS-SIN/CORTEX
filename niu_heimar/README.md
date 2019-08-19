# Docker sets for local deployment

Set of dockers that can be run on any computer for local development, testing, or stand-by subsystem.
- a complete set of dockers for `yggdrasil`: `zookeeper`, `broker`, `schema_registry`, `connect`, `control_center`, and `rest_proxy`
- a `jotunheimr` docker with `APOC, Graph Algorithms, GraphQL, and Streams`
libraries installed, plus `halin`

## A. Run `yggdrasil`

### Start `yggdrasil`:
- On Linux/Mac OS X:

      ./start_yggdrasil.sh

- Windows:

      ./start_yggdrasil.sh <local_ip>

  for example:

      ./start_yggdrasil.sh 10.0.1.119

### Test from another computer (Ubuntu 18.04, Windows 10, Mac OS X)

`remote_ip` is where the `yggdrasil` instance running

    ./test_yggdrasil.sh <remote_ip>

for example:

    ./test_yggdrasil.sh 10.0.1.119


## B. Run `jotunheimr`

  `neo4j_dir` is where the database storage is
  `yggdrasil_host` is where the `yggdrasil` instance running

    ./start_jotunheimr.sh <neo4j_dir> <yggdrasil_host>
