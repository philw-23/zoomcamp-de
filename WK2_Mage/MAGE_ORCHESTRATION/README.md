# Intro To Orchestration

 For this course, we will be using Mage AI for orchestration of our data workflows. The structure of this section will be to utilize Mage AI to automate workflows in order to extract, transform, and load (ETL) data to a Postgres database.
 
 <!-- ## What is Orchestration?

 Orchestration can be defined as "a process of dependency management facilitated through automation". The data orchestrator can manage the following aspects of data pipelines:
 * Scheduling
 * Triggering
 * Monitoring
 * Resource Allocation

 Data workflows are built up via sequential steps. In Mage AI terms:
 * Steps = Tasks to be performed
 * Workflows = DAGs (Directed acyclic graphs)

 A good orchestrator handles:
 * Workflow management
 * Automation
 * Error handling
 * Data recovery
 * Monitoring + Alerting on failures
 * Resource optimization
 * Observability (visibility into every part of data pipeline)
 * Debugging of data pipelines
 * Compliance, auditing, logging

## What is Mage?

Mage is an open source pipeline tool for transforming and integrating data.

Structure:
* Projects (like a github repo, contains all the code for project)
* Pieplines (these are like DAGs)
  * Workflow that executes some data operation
  * Contains blocks written in Python, SQL, R, etc.
* Blocks (these are what make up transformations)
  * Represented as .yml files
  * Dependencies are managed through Mage
  * Can utilize blocks in many different pipelines within a project
* These Export, Transform, and Load data

Blocks are independent entities that are testable on their own. Key features of engineering best practices include:
* In line testing + debugging
* Notebook style formatting
* Transofmration in one place
* Porting to DBT
* Streaming
* DAGs without duplicate functions

## Structure of a Mage Block

* Imports: packages needed
* Decorator: describes what type of function is being executed
* Function: executes an operation that returns a dataframe
    * Only thing that will return data ran when a block is executed
* Test/Assertion: will be executed on the result of the test
    * @test is the decorator for this -->

## Configuring Mage

It is recommended to install and use mage through docker containers, as this enables customization and versioning to be portable across machines. Mage also details some information on docker and other installation methods on their website [here](https://docs.mage.ai/getting-started/setup#docker-compose-template). In this section, we will utilize a network of a Mage container and Postgres container established using the `mage-container.yml` docker compose file. The file contains notes on the specific container configuration options to be executed on initiation

The `mage-container.yml` also references the `Dockerfile` - it serves as a base configuration for the Mage container in the network. The raw file is shown below with comments and additional notes on the arguments

```
FROM mageai/mageai:latest

# NOTE: this is empty for now, if we need additional packages we can install them from here
# The mage container comes preloaded with a number of packages
COPY requirements.txt ${USER_CODE_PATH}requirements.txt 

RUN pip3 install -r ${USER_CODE_PATH}requirements.txt
```
* `FROM` specifies the base container to load from
* `COPY` will copy the `requirements.txt` file to our `USER_CODE_PATH` (defined in docker compose)
* `RUN` will run the command to install additional packages from `requirements.txt` in mage

Mage may prompt during use that a newer version or update is available to install. The latest image can be pulled from docker to use with the following command
```bash
$ docker pull mageai/mageai:latest
```

The Dockerfile and `.yml` file make a number of references to initial environment variables, which are detailed in the `dev.env` file and shown below. Note that these can also be defined for a postgres connection after Mage is initiated (tutorial [here](https://www.analyticsvidhya.com/blog/2024/09/setup-mage-ai-with-postgres/)), but this is more practical for already existing postgres instances (utilizing environment variables as described in these notes can also work with postgres instances that already exist)
```
# These are required variables for Mage to connect to postgres!
POSTGRES_DBNAME=postgres # Name for database in postgres
POSTGRES_SCHEMA=mage # (OPTIONAL) Schema to use for mage in Postgres
POSTGRES_USER=postgres # Login user for Postgtres
POSTGRES_PASSWORD=postgres # Login password for postgres
POSTGRES_HOST=postgres # Host for postgres
POSTGRES_PORT=5432 # Port for postgres

# Other variables used
PROJECT_NAME=mage-zoomcamp # Mage Project Name
```

We will actually use a file named `.env` for sharing environment variables with our docker network (this is standard for production applications), however it is bad practice to include this file in git repos for projects as sensitive information such as API keys may be added later. To avoid this, we can utilize the following command to write the initial safe to share starting variables from our `dev.env` file to the `.env` file. Note that the `.env` will also be added to `.gitignore` to prevent it from being pushed to git
```bash
$ cp dev.env .env
```

Our Mage/Postgres network can be initiated by running the following command. Note that this will build any necessary subcontainers within the file (equivalent of `docker build`) that have not previously been built
```bash
$ docker compose -f mage-container.yml up
```

Upon loading mage, we initially set up a `dev` profile under the `io_config.yml` that can be found in the project files directory. We will use [jinja syntax](https://docs.coalesce.io/docs/reference/jinja/jinja-syntax/) as shown below to load our environment variables to this profile
```yml
dev: # Dev profile - define at bottom after default
  POSTGRES_CONNECT_TIMEOUT: 10
  POSTGRES_DBNAME: "{{ env_var('POSTGRES_DBNAME') }}"
  POSTGRES_SCHEMA: "{{ env_var('POSTGRES_SCHEMA') }}"
  POSTGRES_USER: "{{ env_var('POSTGRES_USER') }}"
  POSTGRES_PASSWORD: "{{ env_var('POSTGRES_PASSWORD') }}"
  POSTGRES_HOST: "{{ env_var('POSTGRES_HOST') }}"
  POSTGRES_PORT: "{{ env_var('POSTGRES_PORT') }}"
```

The advantage of defining these variables in a profile is that the profile can then be referenced to automatically use the parameters in specific data blocks.

## Example Pipeline - Write to Postgres

An example pipeline for downloading taxi data and writing to Postgres using mage can be found in the `api_to_postgres` folder. Instructions on loading this into mage can be found [here](https://docs.mage.ai/guides/pipelines/importing-pipelines)