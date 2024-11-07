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

## Partioning and Clustering Data

### Partitioning Data

 Data in BigQuery can be paritioned on specific columns boost performance. Generally these should be columns that commonly appear as ranges or filters, such as `creation_date` in a table related to Stack Overflow posts. This enables BigQuery to ignore processing for large chunks of data if a partition is filtered out, which can lower costs and increase speed. Partitioning generally does not provide much benefit and may in fact reduce performance for datasets < 1 GB in size. The below command can be used to create a partitioned table in BigQuery
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

Data in BigQuery can be partitioned using the following column types
* Time Unit column - Daily (default), Hourly, Monthly, Yearly
* Ingestion Time
fdsdgfddafg
The number of partitions is limited to 4000, so certain partitions may need to be set to expire (details [here](https://cloud.google.com/bigquery/docs/managing-partitioned-tables)) if using an hourly or daily partition on large datasets. BigQuery will delete data from a partition when it expires

### Clustering Data

Clustering is a method which sorts groups within a dataset so that the rows are colocated next to each other. Up to four columns can be specified for clustering in a dataset. When specifying cluster columns, the data will be sorted in the order of the columns provided. Clustering data improves filter and aggregate queries, and similarly to partitioning does not provide benefit for smaller datasets (< 1 GB in size). Cluster columns can be of the following datatypes:
* DATE
* BOOL
* GEOGRAPHY
* INT64
* NUMERIC
* BIGNUMERIC
* STRING
* TIMESTAMP
* DATE

Returning to the Stack Overflow example again, rows with the same tags ("Android", "Linux", "SQL", etc.) would be clustered together in the dataset if a cluster was set on this column. If the data is partitioned, clusters will also exist within each partition. This is particularly helpful with columns that are frequently used in `WHERE` clauses, as certain clusters can avoid being processed to lower query costs and increase performance. We can create a cluster by using the `CLUSTER BY` argument in our `CREATE OR REPLACE TABLE` command
```sql
CREATE OR REPLACE TABLE '<gcp project>.<bigquery dataset name>.<table name>'
CLUSTER BY
    <cluster_col_1>, <cluster_col_2>, ...
AS
-- Example SQL command to load data 
SELECT * FROM <gcp project>.<bigquery dataset name>.<table name>
```

When new data is added to a dataset, it will impact the clusters that have already been created. Generally this impacts the sort properties the cluster adds to the table. To account for this, BigQuery will perform automatic re-clustering in the background to repair the sort properties. There is no cost incurred from BigQuery as a result of this

### Partitioning vs. Clustering Datasets

Generally, clustering may be a better fit for your data than partitioning (or should be combined with partitioning) if:
* You need more granularity than can be provided alone by partitioning data
* You do not need partition level management - ex: deleting, creating, moving between storage
* Queries will use filters or aggregation on multiple columns
* Cardinality of the number of values in a column or column group is large

Generally, partitioning will be a better fit for your data than clustering if:
* Partitioning results in large data groupings (> 1 GB in size) 
* You require the ability to do partition level management
* Partitioning creates a manageable number of data groupings (< 4000)
* Data operations do not impact a large number of created partitions in the dataset

## Best Practices in BigQuery

BigQuery optimization comes from minimizing cost of queries and increasing performance. There is documentation on [cost controls](https://cloud.google.com/bigquery/docs/best-practices-costs) from google here, but some general strategies for cost reduction of queries are shown below
* Avoid using `SELECT *` when pulling data
* Perform a [dry run](https://cloud.google.com/bigquery/docs/running-queries#dry-run) of queries before executing them
* Use clustering and partitioning in tables
* Utilize streaming inserts to tables with caution
* Materialize query results in stages - ex: utilize a temp table instead of using a CTE in multiple places

For query performance, the following are good strategies for optimization:
* Filter on partitioned columns
* Denormalize data
  * Details are linked above - but involves including key columns or aggregations from other tables in a commonly queried table
* Use of external data sources should be minimized
* Filter and reduce data before using a join
* Do not treat `WITH` clauses as prepared statements
* Avoid oversharding ([sharding](https://www.digitalocean.com/community/tutorials/understanding-database-sharding) detailed here) tables 
* Avoid JavaScript user defined functions (UDFs)
* Use approximate aggregation functions (HyperLogLog++)
* Perform `ORDER BY` in final query
* Optimize join patterns
* Place tables in the following order (by row count)
  * Largest Table
  * Smallest Table
  * Remaining Tables in descending size

## BigQuery Internals

BigQuery stores data in a columnar format, utilizing a cheap data store known as Colossus. This separation from the compute engine helps to keep storage cost of data low. Within BigQuery data centers, there is a network layer linked to Colossus known as Jupiter that provides ~ 1 TB/s network speeds, which enables fast transfer of data to the compute engine. The query execution engine is known as Dremel - which divides your query into a tree structure that separates your query in a way that enables various nodes to execute pieces of the query

Conversely to something like a `.csv` file that stores records in a **row-oriented** format, BigQuery stores data in Colosus with a **column-oriented** format where rows may appear in multiple places for each column. This is advantageous as most queries only target a few columns, and will help improve the performance of aggregations performed on specific columns. Internally when a query in row-oriented form is provided to BigQuery, it converts it to a column-oriented version that is passed down through Mixer and Leaf nodes to be executed against specific chunks of the dataset in Colossus. Results from Colossus are then passed back through the Leaf and Mixer nodes to produce the overall result for the original query. Borg (google precursor to Kubernetes)is the overall orchestration engine that allocates hardware resources for the Mixer and Leaf nodes. The breakdown of the query across multiple nodes is the main reason that BigQuery can provide good performance on large datasets. 

Below are some good resources describing the internals of BigQuery in more detail:
* [BigQuery under the hood](https://cloud.google.com/blog/products/bigquery/bigquery-under-the-hood)
* [Google BigQuery 101](https://sarasanalytics.com/blog/what-is-google-bigquery/#Google_BigQuery_Architecture)
   