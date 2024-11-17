# Analytics Engineering

Analytics Engineering serves as sort of a hybrid field between Data Analytics and Data Engineering. Data Engineers server in more of a software engineering role in data architecture development, whereas Data Analysts focus heavily on interpretation and consumption of results. An Analytics Engineer can bridge the gap between these two fields - providing good software engineering practices to the analytics and machine learning efforts of Data Analyts and Data Scientists.

Analytics Engineers work across all areas of the data ingestion and presentation process, including
* Data Loading
* Data Storing
* Data Modeling
* Data Presentation

The focus in this course for Analytics Engineering will be on **Data Modeling** and **Data Presentation**

## Data Modeling

Two major methods exist for obtaining and integrating data into a datawarehouse
* Extract, Transform, Load (ETL)
* Extract, Load, Transform (ELT)

In ETL processes the data is transformed prior to being loaded into a datawarehouse. This can have higher cost and be be longer to implement as transformations are applied in the pipeline, but leads to cleaner results in the data warehouse. Conversely ELT pipelines will be faster and more flexible due to data being loaded as is before performing transformations. ELT pipelines can also take advantage of lower storage and compute costs when the data is present in cloud data warehouses

One popular strategy for data modeling is **Kimball's Dimensional Modeling**, focusing on prioritizing user understandability and query performance over non-redundant data. This data modeling strategy focuses on using a star-schema containing facts and dimension tables
* *fact tables* contain measures, metrics, or facts related to business processes such as sales, cost, etc.
* *dimension tables* contain information on business entities such as customer, product, etc.

A useful representation of Kimball's modeling architecture is the kitchen analogy. This describes breaking down a data warehouse architecture and ETL process can be broken down into the following groups
* Stage Area (Sourcing and Stocking)
  * Contains raw data and has limited access by users
* Processing Area (Kitchen)
  * Raw data is processed in data models by data team
  * Focuses on efficiency and ensuring data standards are met
* Presentation Area (Dining Hall)
  * Final data presentation
  * Broad user access by stakeholders

## Configuration of dbt Core

For this course, we will be utilizing dbt core instead of the dbt cloud offering to practice configuration and allow for local development. The following section describes some of the key files and functions for dbt core. 

### dbt Commands

WIP

### Configuration File - dbt_project.yml

The `dbt_project.yml` file indicates to dbt that a directory is a valid dbt project, and provides key information on how to execute the project. Full documentation from dbt on the contents and options for this file can be found [here](https://github.com/dbt-labs/dbt-cloud-snowflake-demo-template/blob/main/dbt_project.yml)

 
This [link](https://github.com/dbt-labs/dbt-cloud-snowflake-demo-template/blob/main/dbt_project.yml) provides a practical example file with common configuration parameters. The key features of this file are highlighted below, with the comments in the link providing additional details on other features

1) `name: 'my_snowflake_dbt_project'` provides the name of the initialized project
2) `profile: 'snowflake_demo_project'` is the profile name from `profiles.yml` (detailed below) that dbt uses for authentication
3) `target-path: 'target'` represents the destination where dbt will store JSON artifacts and compiled SQL
4) `models` tells dbt how to build models, including where to build them, and what schema to write the 

For the models section specifically, below is an example from the linked file with some additional customizations that can be provided (some of the snowflake specific parameters are removed - they can be found [here](https://docs.getdbt.com/reference/resource-configs/snowflake-configs) if interested)
```yml
  my_snowflake_dbt_project: # Project name that matches name parameter from above
      staging: # signifies models stored in the models/staging folder
          +materialized: view
          schema: staging
          tags: "daily"
```
* `+materialized` indicates how the model result should be persisted in the target data warehouse
* `schema` is a schema addon for all models stored in the specified folder (in this case `staging`)
  * It will apply a suffix to the `schema` parameter defined in `profiles.yml` file for the project
  * For example if our `schema` in `profiles.yml` for this project was `analytics`, models in the `staging` folder would be build in a `analytics_staging` schema
* `tags` are values applied to a resource that can be used via resource selection
  * For example, `dbt run --select tag:daily` would run all models in `staging` as they have this tag assigned

### Configuration File - properties.yml (formerly schema.yml)

The `properties.yml` file (formerly know as `schema.yml`, can be named anything) allows you to define metadata and properties for models, sources, and other resources in your project. Full documentation from dbt with an example file that we will be referencing can be found [here](https://docs.getdbt.com/reference/configs-and-properties)

`sources` define the external sources that dbt models are built on. These are often views or tables from the source database. Below is the example from the dbt documentation detailing some of the arguments that can be provided to a source
```yml
sources:
  - name: raw_jaffle_shop
    description: A replica of the postgres database used to power the jaffle_shop app.
    tables:
      - name: customers
        columns:
          - name: id
            description: Primary key of the table
            tests:
              - unique
              - not_null

      - name: orders
        columns:
          - name: id
            description: Primary key of the table
            tests:
              - unique
              - not_null

          - name: user_id
            description: Foreign key to customers

          - name: status
            tests:
              - accepted_values:
                  values: ['placed', 'shipped', 'completed', 'return_pending', 'returned']
```
* `name` indicates the name of the source
* `columns` indicates the columns present in the source table
  * Each column has an `id` and `description` field, and can be provided with test assertions on the data
  * As shown, this can be `unique` for value uniqueness required, `not null` for values being required, and `accepted_values` for restricting values to a certain set
  * A full set of potential tests can be found [here](https://docs.getdbt.com/reference/resource-properties/data-tests)

`models` defines the properties and configurations for dbt models in a project. Similar to `sources`, key features such as `name`, `columns`, and `tests` can be defined for model outputs. 
```yml
models:
  - name: stg_jaffle_shop__customers
    config:
      tags: ['pii']
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null

  - name: stg_jaffle_shop__orders
    config:
      materialized: view
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: status
        tests:
          - accepted_values:
              values: ['placed', 'shipped', 'completed', 'return_pending', 'returned']
              config:
                severity: warn
```

We note the `config` argument provided in the above yml output. This is an available option for both `sources` and `models` definitions in the `properties.yml` file. These arguments allow controlling configuration settings for things such as how a model is materialized, persistence of results, and how frequently to check source data for freshness. A full list of config options for [models](https://docs.getdbt.com/reference/model-configs) and [sources](https://docs.getdbt.com/reference/source-configs) are linked

### Configuration File - profiles.yml

When running a dbt model, dbt will read the `dbt_project.yml` file to find the `profile` name that will be used for connecting. Documentation with additional details from dbt can be found [here](https://docs.getdbt.com/docs/core/connect-data-platform/connection-profiles) 

An example file with details on various connection types and arguments can be found [here](https://github.com/RealSelf/dbt-source/blob/development/sample.profiles.yml). We will use the Postgres [Mr. Robot](https://en.wikipedia.org/wiki/Mr._Robot) themed profile example shown in this example file to detail some of the key arguments available
```yml
mr-robot:
    outputs:
        dev:                   
            type: postgres
            threads: 2
            host: 87.65.43.21
            port: 5439
            user: mr_robot
            pass: password1
            dbname: warehouse
            schema: dbt_mr_robot  
        prod:                    
            type: postgres
            threads: 1
            host: 87.65.43.21
            port: 5439
            user: mr_robot
            pass: password1
            dbname: warehouse
            schema: analytics     
    target: dev
```
* `mr-robot` is the profile connection name that dbt will search for in the `dbt_profile.yml` file for the project to authenticate to the target datawarehouse
* `outputs` are the connections dbt can use to connect to different data warehouses or environments
  * We see that there can be multiple options specified, in this case `dev` and `prod`
  * These are referred to as targets - the `--target` argument in the `dbt run` command can be used to specify a specific target at runtime
* `type` specifies the connection type - Postgres, Redshift, Snowflake, and BigQuery are available options
  * The corresponding dbt package - ex: `dbt-postgres` - will need to be installed in your environment to be able to use a specific connection type
* `threads`is the number of threads teh dbt project will run using
* `host`, `port`, `user`, `pass`, and `dbname` are postgres specific parameters for connecting to the specific instance
  * As indicated in the example file linked, different parameters will be used for different data warehouse types
* `target` signifies the default value to use for run time, in this case the `dev` connection

When `dbt-init` is ran in a folder to create an initial project, dbt will automatically create the `profiles.yml` file in the `~/.dbt/` directory and populate it with your inputs. Subsequent project creations will also have entries added to this file

## Setting up dbt Models

All local models for this course will be defined using the `airflow-env` in the `airflow` directory. The models are then mounted in docker to be accessible for use when running airflow 

### Creating a BigQuery dbt Model

Before creating a local model, we want to ensure our `.env` variables are set so we can utilize them in our project initialization with jinja notation. Given that many of our parameters are specific for development on airflow, we will create a `.envlocal` file that contains the following parameters needed for local development
```
# PostgreSQL
PG_DWH_USER=postgres
PG_DWH_PASSWORD=postgres
PG_DWH_DBNAME=postgres
PG_DWH_PORT=5433

# GCP
GCP_KEY_SOURCE='<path to your gcp key>.json'
GCP_PROJECT_ID=<your gcp project id>
GCP_LOCATION=

# DBT
DBT_DATASET='<your BigQuery dataset name>'
```

The following commands will export the environment variables in the current terminal session, with the latter command setting our `GOOGLE_APPLICATION_CREDENTIALS` variable for local GCP authentication
```bash
$ set -o allexport && source ~/zoomcamp-de/airflow/.envlocal && set +o allexport
$ export GOOGLE_APPLICATION_CREDENTIALS=${GCP_KEY_SOURCE}
```

**Note** these will need to be ran in future sessions prior to any local development being performed. Local development sessions should also not be used for running airflow to prevent conflicts in environment variable definitions

We can create a local model by navigating to our `dbt/` folder and initializing, ensuring that our `airflow-env` is activated
```bash
$ source ~/zoomcamp-de/airflow/bin/activate
$ cd ~/zoomcamp-de/airflow/dbt/
$ dbt init
```
The following responses should be provided 
* `Enter a name for your project (letters, digits, underscore):` `<enter desired project name>`
* `Which database would you like to use?`: enter `2` for BigQuery
* `Desired authentication method option:` enter `1` for OAUTH
  * This will enable authentication just by setting the `GOOGLE_APPLICATION_CREDENTIALS` variable
* `project (GCP project id):` `{{ env_var('GCP_PROJECT_ID') }}`
* `dataset (the name of your dbt dataset):` `{{ env_var('DBT_DATASET') }}`
* `threads (1 or more)`: `1`
* `job_execution_timeout_seconds [300]:` any value, or enter for default
* `Desired location option`: `1` for US, `2` for EU

The `profiles.yml` file created in `~/.dbt/profiles.yml` should end up looking like this
```yml
zoomcamp_de_bq_model: # Project name provided to dbt init
  outputs:
    dev:
      dataset: '{{ env_var(''DBT_DATASET'') }}'
      job_execution_timeout_seconds: 300
      job_retries: 1
      location: US
      method: oauth
      priority: interactive
      project: '{{ env_var(''GCP_PROJECT_ID'') }}'
      threads: 1
      type: bigquery
  target: dev
```

You can then test a successfull setup by entering your project and running the `dbt debug` command

### Creating a Postgres dbt Model

**Note:** we can run only our `postgres-dwh` service from our airflow container for local development by specifying the service name in the command
```bash
$ docker compose up postgres-dwh
```

We initialize our project for a postgres connection with the following commands, assuming we have already exported all our environment variables as defined above
```bash
$ cd ~/zoomcamp-de/airflow/dbt/
$ dbt init zoomcamp_de_postgres_model
```

When prompted, the following inputs should be used. Note that the password entry will not show in terminal, but the value provided is captured
```
20:34:57  Setting up your profile.
Which database would you like to use?
[1] postgres
[2] bigquery

(Don't see the one you want? https://docs.getdbt.com/docs/available-adapters)

Enter a number: 1
host (hostname for the instance): localhost
port [5432]: {{ env_var('PG_DWH_PORT') | int}}
user (dev username): {{ env_var('PG_DWH_USER') }}
pass (dev password): {{ env_var('PG_DWH_PASSWORD') }}
dbname (default database that dbt will build objects in): {{ env_var('PG_DWH_DBNAME') }}
schema (default schema that dbt will build objects in): ny_taxi
threads (1 or more) [1]: 1
```
* `port` must be converted to an int type for dbt to connect

The resulting `profiles.yml` file should look like this
```yml
zoomcamp_de_postgres_model:
  outputs:
    dev:
      dbname: '{{ env_var(''PG_DWH_DBNAME'') }}'
      host: localhost
      pass: '{{ env_var(''PG_DWH_PASSWORD'') }}'
      port: '{{ env_var(''PG_DWH_PORT'') | int }}'
      schema: ny_taxi
      threads: 1
      type: postgres
      user: '{{ env_var(''PG_DWH_USER'') }}'
  target: dev
```

We note however that the above configuration will only work for local development outside of airflow given that we are using `localhost` as the hostname. To run models from within airflow, we will need to add a second target using a different hostname and port for postgres
```yml
    airflow_prod:
      dbname: '{{ env_var(''PG_DWH_DBNAME'') }}'
      host: postgres-dwh # utilize service name!
      pass: '{{ env_var(''PG_DWH_PASSWORD'') }}'
      port: 5432 # utilize this port within container
      schema: ny_taxi
      threads: 1
      type: postgres
      user: '{{ env_var(''PG_DWH_USER'') }}'
```

When running models from airflow, we can then specify our desired target using the `--target` argument in `dbt run`
```bash
$ dbt run --target airflow_prod
```

It should also be noted that using our admin postgres credentials for dbt is not best practice in production environments. A dbt user should usually be created in postgres with specific access permissions and roles. The following command will allow you to enter the running postgres container and run commands to set these
```bash
$ docker exec -it <postgres container name> psql -U postgres
```

Documentation on [roles](https://www.postgresql.org/docs/current/user-manag.html) and [privileges](https://www.postgresql.org/docs/current/ddl-priv.html) that can be used for establishing the desired permissions in postgres are linked for here for reference