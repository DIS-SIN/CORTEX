# Sprint #2 BDD tests

## A. Brief description
- A `backend` docker set consisting of a `neo4j` server and a python `app` that execute queries and provide micro services.
- A `nlp` docker running full capability Stanford NLP, to provide sentiment analysis out-of-the-box
- A `bdd` docker that runs end-to-end tests, 1k load tests, and performing normality checks

## B. Usage

### 1. `backend`

  In `/backend` directory, build the docker set, note that at least 8GB RAM is advised. It can also run on host with less memory. Adjust `jotunheirm` service config in `docker-compose.yml` when if needed.

    ./start_backend.sh

  Import the basic datasets:

    ./import_dataset.sh

  Stop it when not using:

    ./stop_backend.sh

  To monitor logs on the host:

    tail -f /tmp/app.log


### 2. `nlp`

  In `/nlp`, build the docker set, note that at least 4GB RAM is advised. It can also run on host with less memory. Adjust `java` JVM `Xmx` argument in `Dockerfile` if needed.

    ./start_nlp.sh

  Stop it when not using:

    ./stop_nlp.sh

### 3. `bdd`

  In `/bdd`, build the docker set, and run it:

    ./start_bdd.sh

  Stop it when not using:

    ./stop_bdd.sh
