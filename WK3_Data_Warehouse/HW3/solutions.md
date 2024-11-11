# Module 3 Homework

## Setup

The airflow DAG `taxi_to_gcs_pipeline` has been set up to pull the 2022 green taxi data from the NYC taxi website and write it to a GCS bucket. The following input parameters are available for the DAG
```
{
    'years': ['2022'], # String list of years to pull data for
    'months': ['01', '02'], # String list of months to pull data for
    'taxi_type': 'green', # Taxi type to pull data for
    'force_overwrite': False # Whether to overwrite existing data if it exists.
}
```

The DAGwill scrape the URLs from the website, validate the existence of our bucket (and create it if now), and then write the data to the bucket. The data is written in chunks with a folder hierarchy of `<year>/<month file>`, and will skip writing data if a matching structure already exists to save time. All data can be forced to be written by setting the DAG parameter `force_overwrite=True`. The corresponding tasks for the DAG are present in the `plugins/tasks/taxi_tasks.py` file

Commands for answers in this HW will be provided using both google cloud console commands and python API calls. The below commands will create the BigQuery external table from our GCS bucket and the standard BigQuery table from our external table

Console:
```SQL
-- Create BigQuery dataset to write data to
CREATE SCHEMA `<your project name>.ny_taxi`;

-- Create external table
CREATE OR REPLACE EXTERNAL TABLE `<your project name>.ny_taxi.green_taxi_2019_external`
OPTIONS(
  format='PARQUET', -- Use parquet format
  uris=['gs://<your bucket name>/2022/*'] -- Get all files from 2022 folder
);

-- Create table from external table
CREATE TABLE ny_taxi.green_taxi_2019 AS (
  SELECT *
  FROM `<your project name>.ny_taxi.green_taxi_2019_external`
);
```

Python:
```python
import os
from dotenv import load_dotenv
from google.cloud import bigquery

#### Create External Table ####
# Load env variables
base_dir = os.path.abspath(os.path.dirname(__file__)) # Get base directory
load_dotenv(base_dir + '/airflow/.env')

# Get env vars
GCP_PROJECT = os.environ.get('GCP_PROJECT_ID') # Get project ID
GCS_LOCATION = os.environ.get('GCP_LOCATION')

# Create BigQuery client
client = bigquery.Client(location=GCS_LOCATION)

# Create BigQuery dataset
dataset_name = 'ny_taxi' # Dataset schema
dataset_path = f'{GCP_PROJECT}.{dataset_name}' # Name to use
dataset = bigquery.Dataset(dataset_path)
dataset.location = GCS_LOCATION
dataset = client.create_dataset(dataset)
print(f'Dataset {dataset_name} successfully created')

# Provide parameters for creation
external_source_format = 'PARQUET' # File format to use
url_list = [f'gs://{GCP_PROJECT}-green-taxi-data/2022/*'] # URI list to use

# Create external config
external_config = bigquery.ExternalConfig(external_source_format)
external_config.source_uris = url_list # Pass list of URLs

# Create table
external_table_name = 'green_taxi_2019_external'
table = bigquery.Table(f'{dataset_path}.{external_table_name}')
table.external_data_configuration = external_config # Set config
table = client.create_table(table)
print(f'External table {dataset_name}.{external_table_name} successfully created')

#### Create Standard Table ####

# Define table name
local_table_name = 'green_taxi_2019'

# Set SQL
sql_query = f'''
    CREATE TABLE {dataset_name}.{local_table_name} AS
    SELECT *
    FROM `{dataset_path}.{external_table_name}`
'''

# Execute query
query = client.query(sql_query)
query.result()
print(f'Standard table {dataset_name}.{local_table_name} successfully created')
```

**Note:** before running the python command, you may need to run the following command unless `GOOGLE_APPLICATION_CREDENTIALS` is defined in your `.env` file
```bash
$ export GOOGLE_APPLICATION_CREDENTIALS='<path to your key>.json
```

Further python code in this HW assumes that all `.env` variables are present and the dataset/tables have been created

## Question 1:

The following code will calculate the total count of records in the 2022 green taxi data. The python code assumes all `.env

Console:
```sql
SELECT COUNT(*)
FROM `ny_taxi.green_taxi_2019`;
```

Python:
```python
from google.cloud import bigquery

# Create BigQuery client
client = bigquery.Client(location=GCS_LOCATION)

# Get env vars
GCP_PROJECT = os.environ.get('GCP_PROJECT_ID') # Get project ID
GCS_LOCATION = os.environ.get('GCP_LOCATION')

# Set table parameters
dataset_name = 'ny_taxi'
table_name = 'green_taxi_2019'

# Define SQL
sql_query = f'''
    SELECT 
        COUNT(*) as count
    FROM `{GCP_PROJECT}.{dataset_name}.{table_name}`
'''

# Execute query
query = client.query(sql_query)
results = query.result()
for row in results: # Iterate to result
    print(f'Total count of records: {row['count']}')
```

Both results return a value of **840,402** for the count of rows in the dataset

## Question 2:

The following queries will indicate the total amount of data processed to get the count of distinct PULocationIDs in the datasets

Console:
```SQL
--Query for counting records in external table
SELECT
  COUNT(DISTINCT PULocationID) AS COUNT_UNIQUE
FROM `ny_taxi.green_taxi_2019_external`;

--Query for counting records in standard table
SELECT
  COUNT(DISTINCT PULocationID) AS COUNT_UNIQUE
FROM `ny_taxi.green_taxi_2019`;

```

**Note:** highlighting the query in the BigQuery console will show a value in the top right for how much data will be processed

Python:
```python
from google.cloud import bigquery

# Create BigQuery client
client = bigquery.Client(location=GCS_LOCATION)

# Set table parameters
dataset_name = 'ny_taxi'
table_name_external = 'green_taxi_2019_external'
table_name_local = 'green_taxi_2019'

# Set dry run in Job Config
job_config = bigquery.QueryJobConfig()
job_config.dry_run = True # Set a dry run for estimation purposes

# Define SQL - External
sql_query = f'''
    SELECT 
        COUNT(DISTINCT PULocationID) AS COUNT_UNIQUE
    FROM `{GCP_PROJECT}.{dataset_name}.{table_name_external}`
'''

# Execute query - External
query = client.query(sql_query, job_config=job_config)
print(f'External query will process {query.total_bytes_processed / (1024 * 1024)} megabytes')

# Define SQL - Standard
sql_query = f'''
    SELECT 
        COUNT(DISTINCT PULocationID) AS COUNT_UNIQUE
    FROM `{GCP_PROJECT}.{dataset_name}.{table_name_local}`
'''

# Execute query - Standard
query = client.query(sql_query, job_config=job_config)
print(f'Standard query will process {query.total_bytes_processed / (1024 * 1024)} megabytes')
```
**Note:** the `dry_run` argument to job config gives estimation on data to process without returning any data

Both results indicate that the estimated amount of data to be processed will be **0 MB for the External Table and 6.41MB for the Materialized Table**

## Question 3:

The following queries will return the total number of records with a fare amount of 0

Console:
```sql
-- Query for $0 fare rows
SELECT
  COUNT(*)
FROM `ny_taxi.green_taxi_2019_external`
WHERE 1=1
  AND fare_amount = 0;
```

Python:
```python
from google.cloud import bigquery

# Create BigQuery client
client = bigquery.Client(location=GCS_LOCATION)

# Get env vars
GCP_PROJECT = os.environ.get('GCP_PROJECT_ID') # Get project ID
GCS_LOCATION = os.environ.get('GCP_LOCATION')

# Set table parameters
dataset_name = 'ny_taxi'
table_name = 'green_taxi_2019'

# Define SQL
sql_query = f'''
    SELECT 
        COUNT(*) as count
    FROM `{GCP_PROJECT}.{dataset_name}.{table_name}`
    WHERE 1=1
        AND fare_amount = 0
'''

# Execute query
query = client.query(sql_query)
results = query.result()
for row in results: # Iterate to result
    print(f'Total count of $0 records: {row['count']}')
```

Both results indicate that **1,622** records have a fare amount of $0

## Question 4:

The optimized strategy for ordering results by PULocationID and filtering based on lpep_pickup_datetime is to **cluster on PULocationID and partition by lpep_pickup_datetime (with a daily partition)**. Since we are frequently filtering on lpep_pickup_datetime by day, this will be applied in a `WHERE` clause in our queries. As a result, by paritioning on lpep_pickup_datetime (daily) we can ignore reading chunks of data that aren't applicable to improve performance and reduce cost. By clustering on PULocationID, we will get the data presorted together by this column in each of our partitions, similar to an `ORDER BY` clause

The following commands will create the partitioned and clustered dataset in BigQuery

Console:
```sql
-- Create partitioned and clustered table
CREATE TABLE `ny_taxi.green_taxi_2019_cluster_partition`
PARTITION BY DATE(lpep_pickup_datetime) -- Parition by date
CLUSTER BY PULocationID -- Cluster by PULocation
AS
  SELECT *
  FROM `ny_taxi.green_taxi_2019_external`;
```

Python:
```python
from google.cloud import bigquery

# Create BigQuery client
client = bigquery.Client(location=GCS_LOCATION)

# Get env vars
GCP_PROJECT = os.environ.get('GCP_PROJECT_ID') # Get project ID
GCS_LOCATION = os.environ.get('GCP_LOCATION')

# Set table parameters
dataset_name = 'ny_taxi'
source_table_name = 'green_taxi_2019_external'
destination_table = 'green_taxi_2019_cluster_partition'

# Define SQL
sql_query = f'''
    CREATE TABLE `{GCP_PROJECT}.{dataset_name}.{destination_table}`
    PARTITION BY DATE(lpep_pickup_datetime)
    CLUSTER BY PULocationID
    AS 
        SELECT 
            *
        FROM `{GCP_PROJECT}.{dataset_name}.{source_table_name}`
'''

# Execute query
query = client.query(sql_query)
results = query.result()
print(f'Created clustered/paritioned table {dataset_name}.{destination_table}')
```

## Question 5:

The following queries will provide the distinct PULocationID between lpep_pickup_datetime
06/01/2022 and 06/30/2022 (inclusive), and for the python code include the dry run results for total memory usage

Console:
```sql
-- Clustered/Partitioned Table
SELECT
  COUNT(DISTINCT PULocationID) AS COUNT_LOC
FROM `ny_taxi.green_taxi_2019_cluster_partition`
WHERE 1=1
  AND lpep_pickup_datetime BETWEEN '2022-06-01' AND '2022-06-30';
```

Python:
```python
from google.cloud import bigquery

# Create BigQuery client
client = bigquery.Client(location=GCS_LOCATION)

# Get env vars
GCP_PROJECT = os.environ.get('GCP_PROJECT_ID') # Get project ID
GCS_LOCATION = os.environ.get('GCP_LOCATION')

# Set table parameters
dataset_name = 'ny_taxi'
table_name_partition = 'green_taxi_2019_cluster_partition'
table_name_local = 'green_taxi_2019'

# Set dry run in Job Config
job_config = bigquery.QueryJobConfig()
job_config.dry_run = True # Set a dry run for estimation purposes

# Define SQL - Partitioned
sql_query = f'''
    SELECT 
        COUNT(DISTINCT PULocationID) AS COUNT_LOC
    FROM `{GCP_PROJECT}.{dataset_name}.{table_name_partition}`
    WHERE 1=1
        AND lpep_pickup_datetime BETWEEN '2022-06-01' AND '2022-06-30';
'''

# Execute query dry run - Partitioned
query = client.query(sql_query, job_config=job_config)
print(f'Partitioned query will process {query.total_bytes_processed / (1024 * 1024)} megabytes')


# Define SQL - Standard
sql_query = f'''
    SELECT 
        COUNT(DISTINCT PULocationID) AS COUNT_LOC
    FROM `{GCP_PROJECT}.{dataset_name}.{table_name_local}`
    WHERE 1=1
        AND lpep_pickup_datetime BETWEEN '2022-06-01' AND '2022-06-30';
'''

# Execute dry run - Standard
query = client.query(sql_query, job_config=job_config)
print(f'Standard query will process {query.total_bytes_processed / (1024 * 1024)} megabytes')
```

Both results indicate the data being processed as **12.82 MB for non-partitioned table and 1.12 MB for the partitioned table**

## Question 6: 

The external table created with a link from our bucket is still being stored in the **GCP Bucket**. Data is not directly read into BigQuery when creating an external table, which is why performance can oftern be lower when querying it

## Question 7:

It is **false** that it is always best practice to cluster your data. For smaller datasets (< 1GB), performance hits could be observed due to additional data created to generate clusters

## (Bonus: Not worth points) Question 8:

Per the BigQuery console, **0 bytes** of data will be processed when the query is ran. This is likely because all that needs to be done is check the number of rows, which BigQuery already has pre-calculated in Storage info (found under table details) for the table


