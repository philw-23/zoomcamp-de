## Module 2 Homework

## Creating a Pipeline

We will use the container created in the WK2 module for this assignment. This can be instantiated with
```bash
docker compose -f ~/zoomcamp-de/WK2_Mage/MAGE_ORCHESTRATION/mage-container.yml up
```

The created `green_taxi_etl` pipeline can be found in this directory and contains comments related to all the functions used for loading, processing, and writing the data. We make use of the following pipeline variables to specify months and years for data pulls in order make our code more flexible for future use. Both are list types, which are supported by mage pipeline variables
```
years: [2020]
months: [10, 11, 12]
```

We will also add print statements to some of the block outputs to answer some of the below questions on transformations and data size at certain steps

To export to postgres, we will use a python exporter with the `dev` profile we defined when creating our mage container. We utilize the following pipeline variables for schema and table names.
```
postgres_schema: mage
postgres_table: green_taxi
```

<!-- The goal will be to construct an ETL pipeline that loads the data, performs some transformations, and writes the data to a database (and Google Cloud!).

- Create a new pipeline, call it `green_taxi_etl`
- Add a data loader block and use Pandas to read data for the final quarter of 2020 (months `10`, `11`, `12`).
  - You can use the same datatypes and date parsing methods shown in the course.
  - `BONUS`: load the final three months using a for loop and `pd.concat`
- Add a transformer block and perform the following:
  - Remove rows where the passenger count is equal to 0 _and_ the trip distance is equal to zero.
  - Create a new column `lpep_pickup_date` by converting `lpep_pickup_datetime` to a date.
  - Rename columns in Camel Case to Snake Case, e.g. `VendorID` to `vendor_id`.
  - Add three assertions:
    - `vendor_id` is one of the existing values in the column (currently)
    - `passenger_count` is greater than 0
    - `trip_distance` is greater than 0
- Using a Postgres data exporter (SQL or Python), write the dataset to a table called `green_taxi` in a schema `mage`. Replace the table if it already exists.
- Write your data as Parquet files to a bucket in GCP, partioned by `lpep_pickup_date`. Use the `pyarrow` library!
- Schedule your pipeline to run daily at 5AM UTC. -->

## Question 1. Data Loading

From our `data.shape` output in the `load_green_taxi_api.py` block of our pipeline, we see the loaded data is **266,855 rows x 20 columns**

## Question 2. Data Transformation

From our print statement in the transformation block, we see that after filtering the data has **139,370 rows**

## Question 3. Data Transformation

The following syntax is correct for creating a date columns from a datetime column
```python
data['lpep_pickup_date'] = data['lpep_pickup_datetime'].dt.date
```

## Question 4. Data Transformation

From our print statement in the transformer block, we see that the unique vendor IDs remaining after filtering are: **1 or 2**

## Question 5. Data Transformation

From our print statement in the transformer block, we see that **4 columns** had to be converted to camel case

## Question 6. Data Exporting

<!-- Once exported, how many partitions (folders) are present in Google Cloud?

* 96
* 56
* 67
* 108 -->


