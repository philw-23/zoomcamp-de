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

To export to GCS, we will add another two variables for `bucket_suffix` and `bucket_table_name` that we will use to load our partitioned bucket to GCS. We will utilize the `validate_bucket` function from our `shared.py` file to create this bucket
```
bucket_suffix: green-taxi-bucket
bucket_table_name: green_taxi_data
```

To add the refresh, we set a schedule trigger to run at 5AM UTC

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

After exporting, we see that there are 95 individual date files present, with the observation that there are three dates that are not in 2020. If we count the additional top level folder, there are **96 folders** created in our cloud bucket


