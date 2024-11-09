import pandas as pd
import os
from datetime import datetime
from airflow import DAG
from airflow.decorators import task
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

'''
    Task to download single URL of taxi data for testing
'''
@task
def download_taxi_data():
    # URL objects
    base_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/'
    data_url = 'green_tripdata_2019-11.csv.gz'

    # Download data
    df = pd.read_csv(
        base_url + data_url,
        sep=',',
        compression='gzip'
    )

    # Return data
    return df

'''
    Task to write df to postgres DWH
'''
@task 
def write_taxi_data(data):
    # Build SQLAlchemy URL
    pg_url = URL(
        drivername='postgresql',
        username=os.environ.get('PG_DWH_USER'), # Get user from env vars
        password=os.environ.get('PG_DWH_PASSWORD'), # Get password from env vars
        host='postgres-dwh', # use service name from host when within the container
        port=5432, # Container port for postgres
        database=os.environ.get('PG_DWH_DBNAME'), # Get dbname from env vars
    )

    # Build engine
    pg_engine = create_engine(pg_url)

    # Write data
    with pg_engine.connect() as conn:
        data.to_sql(
            name='test_green_taxi_data', # Table to write to
            con=conn,
            if_exists='replace',
            index=False
        )

'''
    Define DAG for writing data
'''
with DAG(
    dag_id='test_green_taxi_to_postgres', # Name for dag
    start_date=datetime(2024, 1, 1), # When to start runs
    schedule_interval=None, # Set schedule
    catchup=False # Whether to catchup with failures
):
    # Tasks to run
    data = download_taxi_data()
    write_taxi_data(data)