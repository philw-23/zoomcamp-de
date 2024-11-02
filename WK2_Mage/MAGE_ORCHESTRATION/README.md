# Intro To Orchestration

 For this course, we will be using Mage AI for orchestration of our data workflows. The structure of this section will be to utilize Mage AI to automate workflows in order to extract, transform, and load (ETL) data to a Postgres database.
 

## Configuring Mage

It is recommended to install and use mage through docker containers, as this enables customization and versioning to be portable across machines. Mage also details some information on docker and other installation methods on their website [here](https://docs.mage.ai/getting-started/setup#docker-compose-template). In this section, we will utilize a network of a Mage container and Postgres container established using the `mage-container.yml` docker compose file. The file contains notes on the specific container configuration options to be executed on initiation

The `mage-container.yml` also references the `Dockerfile` - it serves as a base configuration for the Mage container in the network. The raw file is shown below with comments and additional notes on the arguments

```
FROM mageai/mageai:latest

# NOTE: this is empty for now, if we need additional packages we can install them from here
# The mage container comes preloaded with a number of packages
COPY requirements.txt ${USER_CODE_PATH}requirements.txt 

RUN pip3 install -r ${USER_CODE_PATH}requirements.txt
```
* `FROM` specifies the base container to load from
* `COPY` will copy the `requirements.txt` file to our `USER_CODE_PATH` (defined in docker compose)
* `RUN` will run the command to install additional packages from `requirements.txt` in mage

Mage may prompt during use that a newer version or update is available to install. The latest image can be pulled from docker to use with the following command
```bash
$ docker pull mageai/mageai:latest
```

The Dockerfile and `.yml` file make a number of references to initial environment variables, which are detailed in the `dev.env` file and shown below. Note that these can also be defined for a postgres connection after Mage is initiated (tutorial [here](https://www.analyticsvidhya.com/blog/2024/09/setup-mage-ai-with-postgres/)), but this is more practical for already existing postgres instances (utilizing environment variables as described in these notes can also work with postgres instances that already exist)
```
# These are required variables for Mage to connect to postgres!
POSTGRES_DBNAME=postgres # Name for database in postgres
POSTGRES_SCHEMA=mage # (OPTIONAL) Schema to use for mage in Postgres
POSTGRES_USER=postgres # Login user for Postgtres
POSTGRES_PASSWORD=postgres # Login password for postgres
POSTGRES_HOST=postgres # Host for postgres
POSTGRES_PORT=5432 # Port for postgres

# Other variables used
PROJECT_NAME=mage-zoomcamp # Mage Project Name
```

We will actually use a file named `.env` for sharing environment variables with our docker network (this is standard for production applications), however it is bad practice to include this file in git repos for projects as sensitive information such as API keys may be added later. To avoid this, we can utilize the following command to write the initial safe to share starting variables from our `dev.env` file to the `.env` file. Note that the `.env` will also be added to `.gitignore` to prevent it from being pushed to git
```bash
$ cp dev.env .env
```

Our Mage/Postgres network can be initiated by running the following command. Note that this will build any necessary subcontainers within the file (equivalent of `docker build`) that have not previously been built
```bash
$ docker compose -f mage-container.yml up
```

Upon loading mage, we initially set up a `dev` profile under the `io_config.yml` that can be found in the project files directory. We will use [jinja syntax](https://docs.coalesce.io/docs/reference/jinja/jinja-syntax/) as shown below to load our environment variables to this profile
```yml
dev: # Dev profile - define at bottom after default
  POSTGRES_CONNECT_TIMEOUT: 10
  POSTGRES_DBNAME: "{{ env_var('POSTGRES_DBNAME') }}"
  POSTGRES_SCHEMA: "{{ env_var('POSTGRES_SCHEMA') }}"
  POSTGRES_USER: "{{ env_var('POSTGRES_USER') }}"
  POSTGRES_PASSWORD: "{{ env_var('POSTGRES_PASSWORD') }}"
  POSTGRES_HOST: "{{ env_var('POSTGRES_HOST') }}"
  POSTGRES_PORT: "{{ env_var('POSTGRES_PORT') }}"
```

The advantage of defining these variables in a profile is that the profile can then be referenced to automatically use the parameters in specific data blocks.

## Example Pipeline - Write to Postgres

An example pipeline for downloading taxi data and writing to Postgres using mage can be found in the `api_to_postgres` folder. Instructions on loading this into mage can be found [here](https://docs.mage.ai/guides/pipelines/importing-pipelines)

## Example Pipeline - Interface with GCP

We will add a few variables to our `.env` file for interfacing with GCP
* `GCP_PROJECT` is the Project ID for our GCP project
* `GCS_LOCATION` is the location we will use for any GCS storage buckets

Two pipelines are present in this repo
* `api_to_gcs` contains code for writing our nyc taxi data to both a partitioned and unpartitioned file in a GCS bucket

Generally, we also note that environment variables can be accessed in Mage via python using the `os` package as shown below. Examples of this will be shown in the example `api_to_gcs` and `gcs_to_bigquery` pipelines
```python
import os

env_var_value = os.getenv('<your variable key>')
```

In order to authenticate to GCP with mage, we will pass the location of our mirrored service account key path as the `GOOGLE_SERVICE_ACC_KEY_FILEPATH` value in `io_config.yml`. This will allow all GCP interface connctions to authenticate using this key via the default profile. To avoid complications and standardize locations for our datasets, we will also set the `GOOGLE_LOCATION` in the default profile to use a location from our `.env` file. These updates are shown below, and note these environment variables were added after the fact to our `.env` file and are not in `dev.env`
```yaml
GOOGLE_SERVICE_ACC_KEY_FILEPATH: "{{ env_var('KEY_DEST') }}"
GOOGLE_LOCATION: "{{ env_var('GCS_LOCATION') }}" # Optional
```

A bigquery dataset and gcs bucket can be created before running this pipeline, but we will perform existence checks and creation operations using python within mage. These functions can be found in the `shared.py` in this repo. Instructions on loading custom files into your mage pipeline can be found in the docs [here](https://docs.mage.ai/development/dependencies/custom-files). The command to import these functions for use in this mage project is
```python
from mage_zoomcamp.utils.shared import validate_bigquery, validate_bucket
```

The required packages for the create/validate operations are shown below, and will be added in the `requirements.txt` file so they are installed at initialization of the docker network
```
google-cloud-storage
google-cloud-bigquery
```

## Pipeline Variables
Run variables can be defined for a pipeline and can be accessed via code blocks within it. Mage has some documentation [here](https://docs.mage.ai/getting-started/runtime-variable) on defining/accessing these. Generally, these are defined within the `Variables` section of the right hand menu when edited a pipeline and can be accessed in python blocks via `**kwargs` as shown below
```python
var_value = kwargs['<var_key>']
```

The `gcs_to_bigquery` pipeline in this repo shows an example of a variable being used for the bigquery dataset name and bigquery table name. The values used are shown below
```
bq_dataset_name: ny_taxi
bq_dataset_table: yellow_cab_data
```

## Running Mage with Terraform

Mage has some supporting documentation for this shown [here](https://docs.mage.ai/production/deploying-to-cloud/using-terraform), and some of the course videos describe the end result in more detail. This is not covered in this repo, and will instead be explored more in future projects

