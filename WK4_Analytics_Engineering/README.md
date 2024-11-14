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

## Setting up dbt Models

All local models for this course will be defined using the `airflow-env` in the `airflow` directory. The models are then mounted in docker to be accessible for use when running airflow 

### Creating a BigQuery dbt Model

Before creating a local model, we want to ensure our `.env` variables are set so we can utilize them in our project initialization with jinja notation. The following commands will export the environment variables in the current terminal session, with the latter command setting our `GOOGLE_APPLICATION_CREDENTIALS` variable for local GCP authentication
```bash
$ set -o allexport && source ~/zoomcamp-de/airflow/.env && set +o allexport
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

You can then test a successfull setup by entering your project and running the `dbt debug` command