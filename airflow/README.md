# Airflow

This document details setting up Apache Airflow for orchestration of workflows in code for Week 3 and beyond

## Setup and Configuration

### Python Environment

For local development of DAGs and code, a new virtual environment named `airflow-env` was set up. The following commands will create and activate the venv
```bash
$ python3 -m venv airflow-env
$ source airflow-env/bin/activate
```

It is reccomended to upgrade the `pip`, `wheel`, and `setuptools` packages before installing packages in order to improve install time. This is especially important for packages such as `dbt-core` with heavy dependency checks. The following command will upgrade these in `airflow-env`
```bash
$ python3 -m pip install --upgrade pip wheel setuptools
```

The following packages were installed in this virtual environment using `pip3`. They are also installed in airflow by specifying an install of the `requirements_local.txt` file in our Dockerfile
```
apache-airflow
apache-airflow-providers-google
apache-airflow-providers-common-sql
google-auth
google-cloud-storage
google-cloud-bigquery
pyarrow
pandas
requests
lxml
beautifulsoup4
dbt-core
dbt-bigquery
```

**Note:** if you are having difficulty with package version resolution when installing `requirements_local.txt`, the following commands can be ran to install each package individually. This may help resolve issues with the installation trying to check compatibility of all packages simultaneously
```bash
$ sudo chmod +x ./shell_pip_install.sh
$ ./shell_pip_install.sh
```

### Airflow Configuration

Airflow adds certain folders to the `PYTHONPATH` such that data between them is transferrable and accessible via import calls. We will create these three folders in our airflow directory
```bash
$ cd airflow
$ mkdir -p ./dags ./logs ./plugins ./dbt
```
* `./dags` is where our dag files will be kept
* `./logs` is for logs from airflow
* `./plugins` is where custom scripts, operators, and plugins can be kept
* `./dbt` is where dbt scripts will be stored for use in later weeks
  * This is not explicitly added to `PYTHONPATH`, but can be via the Dockerfile
  * The above is not required as we can use full paths to run dbt models

A `dev.env` file in this directory contains the environment variables that will be needed for compiling the file. Once all the values have been filled in, the following will copy the values to the `.env` file we will use with docker compose
```bash
$ cp dev.env .env
```

Note that on a linux machine, we will want to set the airflow UID using our host user id. This will prevent the container and files from being created with `root` ownership. The output of the below command should be put in the `.env` file for `AIRFLOW_UID`
```bash
$ echo -e "AIRFLOW_UID=$(id -u)"
```

Next, we download the most up to date docker compose file from Apache
```bash
$ curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
```

Most of this file can be used as-is, but critical changes are noted in the file! Most notably, we change the build context to use a custom Dockerfile so we can install python packages and dependencies we might need. Specific additional packages are listed in the `requirements.txt` file. With everything set up, we can then compile initially to create an airflow user with the following command
```bash
$ docker compose up airflow-init
```

The `docker compose up` command can then be usef to run the container going forward. The airflow UI can be accessed from `localhost:8080` when the container is running

### Adding Connections

Airflow provides documentation on setting up connection profiles [here](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html). Two methods we will highlight are adding via environment variables and adding through the UI. Note that connections added via environment variables **will not** be stored in the airflow database for persistence between sessions

When defining an environment variable in either a `.env` or `docker-compose` file, airflow will treat any variable in the format `AIRFLOW_CONN_YOUR_CONNECTION` as an airflow connection with the name `your_connection`. These inputs can be provided in a json format (as of airlow 2.3) or a URI format. For example, the json definition of our GCP connection in our `.env` file would look like this
```bash
AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT='{
  "conn_type": "google_cloud_platform",
  "extra": {
    "key_path": "path/to/key_in_airflow.json",
    "project": "<your project id>"
  }
}'
```
* **Note:** Full documentation on available GCP connection options and formatting can be found [here](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/connections/gcp.html)
* **Note:** airflow will by default use the `GOOGLE_CLOUD_DEFAULT` connection when trying to connect to GCP if another connection is not provided

And in `docker-compose.yml`, would look like this
```yml
AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT: >-
  {
      "conn_type": "google_cloud_platform",
      "extra": {
        "key_path": "path/to/key_in_airflow.json",
        "project": "<your project id>"
      }
  }
```

A connection can then be used by utilizing connection hooks provided by Airflow. There are hooks available for common connection types based on the type of transactions being performed - for GCP these include `BigQueryHook` for BigQuery transactions and `GCSHook` for bucket based transactions. The connection specified `AIRFLOW_CONN_YOUR_CONNECTION` is passed to these hook functions as the authentication method for subsequent transactions
```python
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from google.cloud import bigquery, storage

# Create BigQuery hook
bigquery_hook = BigQueryHook(gcp_conn_id='<your connection name>')
bq_client: bigquery.Client = bigquery_hook.get_client() # Create a bigquery client

# Create GCS hook
gcs_hook = GCSHook(gcp_conn_id='<your connection name>')
gcs_client: storage.Client = gcs_hook.get_conn() # Create a gcs client
```

Similar logic can be followed for other available connection types, including [postgres](https://airflow.apache.org/docs/apache-airflow-providers-postgres/stable/_api/airflow/providers/postgres/hooks/postgres/index.html) and [AWS](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/hooks/index.html). A list of airflow provider packages (which will contain interface hooks) can be found [here](https://airflow.apache.org/docs/apache-airflow-providers/packages-ref.html)

A connection can be added through the UI by navigating to `Admin > Connections` on the top bar of the homescreen. When selecting the `+` option to add a new record, a form will pop up where you can manually add connection parameters for a variety of tools. Contrary to defining via an environment variable, connections set up from this screen will persist between airflow sessions

Note that airflow connection parameters **will not** be encrypted unless a valid fernet key is provided using the environment variable `AIRFLOW__CORE__FERNET_KEY` is provided. Once a key is provided, credentials will be encrypted and only accessible with this key - if it is lost or an incorrect key is provided at initialization any saved connection profiles will not be usable. A fernet key can be generated in python with the following code
```python
from cryptography.fernet import Fernet

fernet_key = Fernet.generate_key()
```

### Adding DBT Models

The following additional environment variables should be populated in the `.env` file before launching the airflow container
```bash
DBT_DATASET='<your big query dataset name>'
DBT_PROFILE_SOURCE='<path to your profiles file>.yml'
DBT_PROFILES_DIR='<path to destination folder for profiles.yml>'
DBT_PROFILE_DEST=${DBT_PROFILES_DIR}/profiles.yml'
```
* `DBT_DATASET` is the name of the model dataset to connect to
* `DBT_PROFILE_SOURCE` is the local location of your `profiles.yml` file created by DBT when initializing a project
  * By default, this is stored in `~/.dbt/profiles.yml`, but can be moved to a different location specified by the `DBT_PROFILES_DIR` environment variable
* `DBT_PROFILES_DIR` is the folder location where dbt will search for the `profiles.yml` file
* `DBT_PROFILE_DEST` is destination folder of `profiles.yml` (including filename) in airflow 

**Note:** if there are multiple dbt models being loaded, additional variables for `DBT_DATASET` can be added for each model. If you have a large number of connection profiles you would like airflow to access, it might be easier to hardcode setups rather than set and manage a large number of environment variables. Regardless of strategy, the `DBT_PROFILE_SOURCE` and `DBT_PROFILE_DEST` variables only need to be defined assuming all profile configurations are stored in the `profiles.yml` file

The following should be added to the `docker-compose.yml` file to volume mount the `profiles.yml` file in airflow
```yml
volumes:
  ...
  - ${DBT_PROFILE_SOURCE}:${DBT_PROFILE_DEST}
```

A `profile.yml` file must exist locally prior to initialization for the mount to be successful. If you have not created any models locally for development, it is best to comment out the above dbt items in your `docker-compose.yml` file until the local models are created

Examples used in this course for creating BigQuery and postgres dbt models can be found in the WK4_Analytics_Engineering section notes

## Sample DAG

We will use a simple sample DAG to validate that our airflow instance is working. This will write a single month of green taxi data to a `test_green_taxi_data` table in our `postgres-dwh` service. The dag can be found in DAGs and is named `taxi_to_postgres_test.py`

DAGs can be ran by opening the airflow web UI and selecting the play button on the right side of the screen under "Actions" for a specified DAG. Logs can be found by clicking on one of the buttons under "Runs", selecting a specific Run Id, and selecting "Event Log" on the top bar. Detailed stack trace for a specific task can be found by clicking on a specific block after selecting a Run Id and then selectiong "Logs" on the top bar. To verify that data was written to the DWH, we use `pgcli` from our `zoomcamp-env` in a new terminal
```bash
$ source ~/zoomcamp-de/zoomcamp-env/bin/activate
$ pgcli -h localhost -u postgres -p 5433
```
* Note we use `-h localhost` and `-p 5433` for accessing the postgres database from **outside** the container
* We would use `-h postgres-dwh` (service name in docker compose) and `-p 5432` for accessing the postgres database from **inside** the container

We can then run the `\d` command to see that we have a table
```
+--------+----------------------+-------+----------+
| Schema | Name                 | Type  | Owner    |
|--------+----------------------+-------+----------|
| public | test_green_taxi_data | table | postgres |
+--------+----------------------+-------+----------+
```

And can run the following SQL command to see we have data
```
$ select count(*) from test_green_taxi_data
+--------+
| count  |
|--------|
| 449500 |
+--------+
```
