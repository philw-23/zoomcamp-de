# Week 1 - Docker and Terraform

## Creating the Image and accessing via Terminal

The docker image used for this experiment can be activated with the following terminal command. Note that the container must be running to access later with other tools
```bash
$ docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v $PWD/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:13
```

The lines in this code perform the following functions
* `-e POSTGRES_USER="root"`: specify login user for postgres
* `-e POSTGRES_PASSWORD="root"`: specify login password for postgres
* `-e POSTGRES_DB="ny_taxi"`: specify database name for postgres
* `-v $PWD/ny_taxi_postgres_data:/var/lib/postgresql/data`: create a volume mount for storing data to access later; `$PWD` gives the current working directory in bash
* `-p 5432:5432`: specify the port for postgres
* `postgres:13`: postgres image being ran

The `postgres_container.sh` file can be also be used to run the docker image. This needs to be converted to be executable using the following command:
```bash
$ sudo chmod +x postgres_container.sh
```

You can access the `ny_taxi_postgres_data` volume mount to view the information available by entering the directory, however you may need to run the following command if permission issues are encountered
```bash
$ sudo chmod a+rwx [path_to_directory]/ny_taxi_postgres_data
```

With the container active, from a new terminal window the `pgcli` package can be used to access the database via command line. The password will need to be provided after running this command
```bash
$ pgcli -h localhost -p 5432 -u root -d ny_taxi
```

Running the following command will show all the tables available in the database. Currently there are none, so the result should be blank
```postgres
\d
```

There were initially the following dependency issues with `psycopg` when trying to connect to the db via `pgcli`
```
ImportError: no pq wrapper ashorthandc' implementation: No module named 'psycopg_c'
- couldn't import psycopg 'binary' implementation: No module named 'psycopg_binary'
- couldn't import psycopg 'python' implementation: libpq library not found
```

These were alleviated by installing the following dependencies
```bash
$ pip3 install "psycopg[binary,pool]"
```

## Obtaining and Writing to Database using Python

Code with comments for pulling and writing the taxi data to files and then postgres can be found in `TaxiDataExploreAndWrite.ipynb`. Alternatively, this can be ran using the `DataIngestion.py` script with user input and the below command. This will be used later with containerization. Note that for either of these scripts to write data, the docker container must be running.

```bash
$ URL="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet"

$ python DataIngestion.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --tb=yellow_taxi_data \
  --url=${URL}
```

After loading the data via the notebook, the following should now be shown when running `\d` after opening a connection to the db with `pgcli`

```
root@localhost:ny_taxi> \d
+--------+------------------+-------+-------+
| Schema | Name             | Type  | Owner |
|--------+------------------+-------+-------|
| public | pickup_locations | table | root  |
| public | yellow_taxi_datas| table | root  |
--+-------+-----------------+-------+-------+
```

Queries can also be made against the tables. The below gets the count of records in the `yellow_taxi_data` table

```
root@localhost:ny_taxi> select count(*) from yellow_taxi_data
+---------+
| count   |
|---------|
| 3066766 |
+---------+
```
## Docker Networks

Generally if you run a docker container, it will not have access to other machines outside of its scope. We can get around this by creating a docker network to run multiple containers with access to each other. This is done via the `docker network create` command. For example, the below will create a docker networkd names "pg-network"

```bash
$ docker network create pg-network
```

Containers can be manually added to the network after activating them, or they can be added via a `--network` flag in the docker run statement. To run our postgres container from previous examples in a specified network, we use the below command

```bash
$ docker run -it \

  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v $PWD/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  --network=pg-network \
  --name pg-database \
  postgres:13
```
* The `--network` flag specifies the network to connect the container to
* The `--name` flag specifies a container name to use

You may encounter errors if a container already exists with a specified name. To list all containers available, we use the command
```bash
$ docker ps -a
```
* Containers can be stopped using the `docker stop` command with the container name
* Containers can be removed using the `docker rm` command with the container name

We can create a pgadmin (postgres query interface) container in our network to access our data in postgres using the following command
```bash
$ docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8080:80 \
  --network=pg-network \
  --name pg-admin \
  dpage/pgadmin4
```

Pgadmin should then be accessible by entering `localhost:8080` on a web browser and logging in using the `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD` credentials. A server can be added (details on adding in the lecture video) will the following parameters from our postgres container definition that will enable a connection and querying of the data
* `General > Name`: `taxi-data`
* `Connection > Host name/address`: `pg-database`
* `Connection > Port`: `5432`
* `Connection > Username`: `root`
* `Connection > Password`: `root`

## Docker Compose

Multiple docker containers can also be ran simultaneously using a docker compose file. All the parameters needed can be specified in the file and the containers will then be ran in the same network with the command
```bash
$ docker compose -f [your_dockerfile_name] up
```

Note that a `-d` flag can also be added to this command to run in detatched mode, which will enable the same terminal to be used. For this experiment, the `postgres-container.yaml` file can be ran with the above command to give access to the pgadmin and postgres database containers. It also contains comments regarding the various sections and commands of the docker compose file structure.

You may run in to permissions issues when trying to run the docker compose file with a pgadmin volume mount. This is documented [here](https://www.pgadmin.org/docs/pgadmin4/latest/container_deployment.html#mapped-files-and-directories), and can be alleviated by granting ownership of the volume mount folder to the pgadmin user in the pgadmin group
```bash
$ sudo chown -R 5050:5050 data/pgadmin/
```
* `-R`: gives ownership to all files and folders in a directory
* `5050:5050`: pgadmin UID and pgadmin GID