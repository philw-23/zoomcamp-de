# Homework 1

## Question 1. Knowing docker tags

Running the following command in bash
```bash
$ docker run --help
```

We see that the "Automatically remove the container and its associated anonymous volumes when it exits" description is for the **`--rm`** command

## Question 2. Understanding docker first run 

We create a `python.Dockerfile` file with `FROM` and `ENTRYPOINT` defined as follows
```
FROM python:3.9
ENTRYPOINT [ "bin/bash" ]
```

We then can run the following command to build the Dockerfile under the image name `python-test`
```bash
$ docker build -f python.Dockerfile -t python-test .
```
* `-f` specifies the Dockerfile to build
* `-t` specifies the image name to use
* `.` sets the build context to the current directory

Finally, we build the docker container with an interactive terminal and obtain the version of `wheel` with the following commands
```bash
$ docker run -it python-test
$ pip show wheel
```
The following output of the second command shows the version of wheel as **`0.44.0`**
```
Name: wheel
Version: 0.44.0
Summary: A built-package format for Python
Home-page: 
Author: 
Author-email: Daniel Holth <dholth@fastmail.fm>
License: 
Location: /usr/local/lib/python3.9/site-packages
Requires: 
Required-by: 
```
Note that this different than the answers from the HW, indicating that the image may have been changed since the assignment was initially published

# Prepare Postgres

We will load our postgres and pgadmin container in order to be able to write the new data
```bash
$ docker compose -f ~/zoomcamp-de/WK1_Docker_Terraform/DOCKER_SQL/postgres-container.yaml up
```
Then we can activate our environment and utilize our previous python script to write the data to postgres. We will write the data to the `hw1_green_taxi` table in postgres
```bash
$ source ~/zoomcamp-de/zoomcamp-env/bin/activate
$ URL="https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2019-09.parquet"
$ python zoomcamp-de/WK1_Docker_Terraform/DOCKER_SQL/DataIngestion.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --tb=hw1_green_taxi \
  --url=${URL}
```

## Question 3. Count records 

The following SQL query will calculate the number of rides that were made completely (pickup and dropoff) on 2019-09-18
```sql
select count(*) from hw1_green_taxi
where 1=1
	-- Need to cast columns to date to compare directly
	and lpep_pickup_datetime::date = '2019-09-18'
	and lpep_dropoff_datetime::date = '2019-09-18'
```

This gives us the result of **`15612`** trips

## Question 4. Longest trip for each day

The following query will give us the day (pickup time only) with the longest trip
```sql
select
	lpep_pickup_datetime::date,
	max(lpep_dropoff_datetime - lpep_pickup_datetime) as total_seconds
from hw1_green_taxi
group by 1 -- group by 1st column
order by 2 desc -- group by 2nd column
```

The first record in this dataset will be the day with the longest trip duration, which is **2019-09-26**. We do note that the time of this trip is **4 days 04:45:02**, which likely could be an error in a ride being closed out.

## Question 5. Three biggest pick up Boroughs

We first check if there are any `null` values in the `PULocationID` column to determine if a left or inner join should be used for the locations table. In this case, there are no `null` values, so we will use an inner join
```sql
select count(*) 
from hw1_green_taxi
where 1=1
	and "PULocationID" is null
```

The following query can then give us the three biggest pickup buroughs (over 50,000) with a pickup date of 2019-09-18. Note that to round to two decimal places, we need a numeric datatype
```sql
select
	p."Borough",
	-- Sum total amound, round to two decimal places
	round(sum(h.total_amount::numeric), 2) as total_fares
from hw1_green_taxi as h
inner join pickup_locations as p
	on h."PULocationID" = p."LocationID"
where 1=1
	-- Ignore unknown borough
	and p."Borough" <> 'Unknown' 
	-- Set pickup date as 2019-09-18
	and h.lpep_pickup_datetime::date = '2019-09-18'
group by 1
-- Use having clause to filter aggregate
having sum(h.total_amount) > 50000
```

This gives us the following result, showing the three boroughs with > 50,000 total amount as **Brooklyn, Manhattan, and Queens**

```
"Borough"	"total_fares"
-----------------------
"Brooklyn"	96333.24
"Manhattan"	92271.30
"Queens"	78671.71
```
## Question 6. Largest tip

Similarly to the previous question where we checked for `null` values in the pickup zone, we check for `null` values in the dropoff zone. As in the previous problem, we see that there are none
```sql
select count(*)
from hw1_green_taxi
where 1=1
	and "DOLocationID" is null
```

The following query will then give us the largest tip with a pickup zone of Astoria in the month of September
```sql
select
	d."Zone",
	max(h.tip_amount) as max_tip
from hw1_green_taxi as h
inner join pickup_locations as p
	on h."PULocationID" = p."LocationID"
inner join pickup_locations as d -- Dropoff
	on h."DOLocationID" = d."LocationID"
where 1=1
	-- Ignore unknown borough
	and p."Borough" <> 'Unknown' 
	-- Filter to September
	and h.lpep_pickup_datetime::date >= '2019-09-01'
	and h.lpep_dropoff_datetime::date < '2019-10-01'
	-- Filter to Astoria
	and p."Zone" = 'Astoria'
group by 1
order by 2 desc
```

The result is that the largest tip given for this criteria is **62.31** on a trip to **JFK Airport**

After this question, we close our postgres containers using the following command
```bash
$ docker compose -f ~/zoomcamp-de/WK1_Docker_Terraform/DOCKER_SQL/postgres-container.yaml down
```

# Terraform

## Question 7. Creating Resources

First, we navigate to to our terraform directory
```bash
$ cd ~/zoomcamp-de/WK1_Docker_Terraform/TERRAFORM_GCP
```

We then create a `.tfvars` file with the necessary variables as described in the `README.md` file in the referenced directory. The following commands can then be ran
```bash
$ terraform init
$ terraform apply -var-file="user-variables.tfvars"
```

This gives the following output (with project name and location hidden). We will not apply any of these changes
```
Terraform will perform the following actions:

  # google_bigquery_dataset.demo_dataset will be created
  + resource "google_bigquery_dataset" "demo_dataset" {
      + creation_time              = (known after apply)
      + dataset_id                 = "test_bq_dataset"
      + default_collation          = (known after apply)
      + delete_contents_on_destroy = false
      + effective_labels           = (known after apply)
      + etag                       = (known after apply)
      + id                         = (known after apply)
      + is_case_insensitive        = (known after apply)
      + last_modified_time         = (known after apply)
      + location                   = "<your location>"
      + max_time_travel_hours      = (known after apply)
      + project                    = "<your project name>"
      + self_link                  = (known after apply)
      + storage_billing_model      = (known after apply)
      + terraform_labels           = (known after apply)

      + access (known after apply)
    }

  # google_storage_bucket.demo-bucket will be created
  + resource "google_storage_bucket" "demo-bucket" {
      + effective_labels            = (known after apply)
      + force_destroy               = true
      + id                          = (known after apply)
      + location                    = "<your location>"
      + name                        = "<your project name>-test-terraform-bucket"
      + project                     = (known after apply)
      + public_access_prevention    = (known after apply)
      + self_link                   = (known after apply)
      + storage_class               = "STANDARD"
      + terraform_labels            = (known after apply)
      + uniform_bucket_level_access = (known after apply)
      + url                         = (known after apply)

      + lifecycle_rule {
          + action {
              + type          = "AbortIncompleteMultipartUpload"
                # (1 unchanged attribute hidden)
            }
          + condition {
              + age                    = 1
              + matches_prefix         = []
              + matches_storage_class  = []
              + matches_suffix         = []
              + with_state             = (known after apply)
                # (3 unchanged attributes hidden)
            }
        }

      + versioning (known after apply)

      + website (known after apply)
    }

Plan: 2 to add, 0 to change, 0 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: 
```