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

## Question 4. Longest trip for each day

## Question 5. Three biggest pick up Boroughs

## Question 6. Largest tip

# Terraform

## Question 7. Creating Resources
