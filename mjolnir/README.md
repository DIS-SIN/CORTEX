# Tool for large data import

Tool to scrape, extract, and import large data into `jotunheimr` via `yggdrasil`

### Create a similar template to `CORTEX/datasets/config.template.ini`:

### Local import:

    ./run_local_import.sh ../datasets 10.0.1.119

### Remote import:

    ./run_remote_import.sh <dataset_directory> <jotunheimr_ip> <yggdrasil_broker_ip> <yggdrasil_schema_registry_ip> <yggdrasil_connect_ip>
