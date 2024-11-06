# Data Warehousing

## What is BigQuery?

There are two primary categories of data processing systems:
1) Online Transaction Processing (OLTP)
2) Online Analytical Processing (OLAP)

OLTP systems tend to be backend database systems that tend to have [normalized](https://learn.microsoft.com/en-us/office/troubleshoot/access/database-normalization-description) structures for fast, performant updates. Conversely, OLAP databases tend to have [de-normalized structures](https://www.splunk.com/en_us/blog/learn/data-denormalization.html) more optimized for reporting and analysis. OLAP database structures can be fed data from multiple sources, including OLTP databases, flat files, web APIs, etc.

BigQuery is an OLAP datawarehouse solution that is offered by google. It does not require servers, and has a lot of machine learning and business intelligence features built in. The BigQuery compute engine is maintained separately from data storage to maximize flexibility and efficiency of the system.

General costing for BigQuery is purely dependent on the volume of data stored and the volume of data queried. It does not charge for creating tables or structures, but there may be additional charges for using more advanced Machine Learning or Business Intelligence features. Full documentation on pricing can be found in Google's documentation [here](https://cloud.google.com/bigquery/pricing)

### Adding and Querying Data

External data sources from GCS can be added to BigQuery using the `CREATE OR REPLACE EXTERNAL TABLE` command. This command will take in URI representation of a specified file type and create a table within a specified project and bigquery dataset. A list of supported filetypes and additional argument options can be found [here](https://cloud.google.com/bigquery/docs/external-data-cloud-storage#sql). Note that the created dataset will not have size (table size or long-term storage size) information available as the data is not actually loaded and stored in BigQuery - it is a connection to the data in GCS
```SQL
CREATE OR REPLACE EXTERNAL TABLE '<gcp project>.<bigquery dataset name>.<table name>'
OPTIONS (
    format = '<file format>',
    uris = ['uri1', 'uri2', ...],
    ...
)
```
* URIs follow the format of `'gs://<bucket name>/<folder name>/<filename>'`
* URIs can be passed with wildcard formats - such as `'2019-*.csv'` to pull `'2019-01.csv', '2019-02.csv', ...`

Note that the above example describes creating an external dataset, but similar syntax is used for creating a standard dataset within BigQuery. Documentation on this can be found [here](https://cloud.google.com/bigquery/docs/tables#sql). External tables may have slower query performance than standard BigQuery tables as it is roughly equivalent to reading the data from source. If higher performance is needed, it is reccomended to create a standard BigQuery table from the external table data using the commands in the documentation link above.

Querying in BigQuery follows similar logic to querying in other SQL databases. The below query takes 100 rows from the `new_york_citibike` public dataset found in `biquery-public-data`. The use of a limit parameter can be useful to preview results and prevent charges from large queries. 
```sql
SELECT station_id, name FROM
bigquery-public-data.new_york_citibike.citibike_stations
LIMIT 100
```

### Partitioning Data

 Data in BigQuery can be paritioned on specific columns boost performance. Generally these should be columns that commonly appear as ranges or filters, such as `creation_date` in a table related to Stack Overflow posts. This enables BigQuery to ignore processing for large chunks of data if a partition is filtered out, which can lower costs and increase speed. The below command can be used to create a partitioned table in BigQuery
 ```sql
CREATE OR REPLACE TABLE '<gcp project>.<bigquery dataset name>.<table name>'
PARTITION BY
    <partition_col_1>, <partition_col_2>, ...
AS
-- Example SQL command to load data 
SELECT * FROM <gcp project>.<bigquery dataset name>.<table name>
 ```
 * SQL command for data load can be any query that returns a result set

Partition information such as storage size and number of rows can be found in the `INFORMATION_SCHEMA.PARTITIONS` table within a BigQuery dataset. More information on available info can be found [here](https://cloud.google.com/bigquery/docs/information-schema-partitions)
```sql
SELECT *
FROM '<bigquery dataset name>.INFORMATION_SCHEMA.PARTITIONS'
WHERE table_name = '<table name>'
```

This view can be useful for viewing if there is bias within partitions - cases where certain partitions are getting far more rows than others. If there is a heavy bias towards specific partitions and data from these partitions is desired in many query results, there may not be a lot of benefit in the partition.

### Clustering Data

Clustering is a method which sorts groups within a dataset so that the rows are next to each other. Using the Stack Overflow example again, rows with the same tags ("Android", "Linux", "SQL", etc.) would be clustered together in the dataset. If the data is partitioned, clusters will also exist within each partition. This is particularly helpful with columns that are frequently used in `WHERE` clauses, as certain clusters can avoid being processed to lower query costs and increase performance. We can create a cluster by using the `CLUSTER BY` argument in our `CREATE OR REPLACE TABLE` command
```sql
CREATE OR REPLACE TABLE '<gcp project>.<bigquery dataset name>.<table name>'
CLUSTER BY
    <cluster_col_1>, <cluster_col_2>, ...
AS
-- Example SQL command to load data 
SELECT * FROM <gcp project>.<bigquery dataset name>.<table name>
```
It is not shown in the above command, but it should be noted that both clustering and partitioning can be used on the same table