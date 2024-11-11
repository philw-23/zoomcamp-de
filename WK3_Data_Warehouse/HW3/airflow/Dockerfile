# Get most recent version
FROM apache/airflow

ENV AIRFLOW_HOME=/opt/airflow

# Need to set user as airflow 
# Note: previously was root, but ran into errors
USER root
RUN apt-get update -qq && apt-get install vim -qqq

# Run below as airflow
USER airflow
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR $AIRFLOW_HOME
