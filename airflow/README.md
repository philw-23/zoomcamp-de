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
