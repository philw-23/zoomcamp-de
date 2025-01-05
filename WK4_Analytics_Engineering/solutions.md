## Module 4 Homework 

### Question 1: 

**What happens when we execute dbt build --vars '{'is_test_run':'true'}'**

Running this command will execute all models in the directory with a **limit of 100 rows applied to models with this variable defined**. In this case, it will be our `stg_green_tripdata` and `stg_yellow_tripdata` models. Note with dbt core however, issues were experienced when using `'true'` vs. `true` when passing the boolean variable

### Question 2: 

**What is the code that our CI job will run? Where is this code coming from?**  

dbt core was used for this section, however the CI job will merge from the **development branch to the main branch** as shown in the video

### Question 3 (2 points)

**What is the count of records in the model fact_fhv_trips after running all dependencies with the test run variable disabled (:false)?**  

The fhv models used for this question are defined as `staging/stg_fhv_data.sql` and `core/fhv_fact_trips`. Note that running these models requires `fhv_2019` to be defined as a source in the `staging/properties.yml` file. Following with the problem statement, a deduplication step was not added

These models can be ran and generated using the following command
```bash
$ dbt run --select +fhv_fact_trips.sql --vars '{"is_test_run": false}'
```

This dataset has **`23,014,060`** rows after completion. The closest answer to this is **`22,998,722`**

### Question 4 (2 points)

**What is the service that had the most rides during the month of July 2019 month with the biggest amount of rides after building a tile for the fact_fhv_trips table and the fact_trips tile as seen in the videos?**

We did not use dbt cloud for this homework, so we will use sql queries to answer this question. The following sql query will give us the count totals for July 2019 for the green and yellow taxi services
```sql
SELECT  
  revenue_month,
  service_type,
  sum(total_monthly_trips) as total_trips
FROM `circular-truck-437316-i2.ny_taxi_core.dm_monthly_zone_revenue`
WHERE 1=1
  AND revenue_month = '2019-07-01'
GROUP BY 1, 2
```

This gives `3,259,902` trips for the yellow service and `415,397` trips for the green service. The following query will give us the result for the fhv service

```sql
SELECT
  '2019-07-01' AS month,
  count(*) as total_trips
FROM `ny_taxi_core.fhv_fact_trips`
WHERE 1=1
  AND pickup_datetime >= '2019-07-01'
  AND pickup_datetime < '2019-08-01'
GROUP BY 1
```

This gives `290,682` as the number of trips for the fhv service for July 2019. Thus, the **Yellow** service has the most trips during this time
