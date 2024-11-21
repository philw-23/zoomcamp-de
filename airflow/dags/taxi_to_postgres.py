import os
import sys
from airflow import DAG
from airflow.decorators import task
from airflow.models.param import Param
from datetime import datetime
from tasks.taxi_tasks import (
    pull_taxi_data,
    write_data_to_postgres
)

with DAG(
    dag_id='taxi_data_to_postgres',
    start_date=datetime(2024, 1, 1),
    schedule=None, # '@daily', # Optional daily schedule
    catchup=False,
    params={
        'months': Param(default=['01', '02', '03', '04', '05', '06', '07', '08', '09',
                                '10', '11', '12']), # Months to pull data for
        'years': Param(default=['2022']), # Years to pull data for
        'taxi_type': Param(default='green'), # Taxi type to pull data for
        'tgt_schema': Param(default='ny_taxi')
    },
    tags=['data-zoomcamp']
) as dag:
    
    # Get runtime parameters
    @task
    def get_param(key_val, **kwargs):
        params = kwargs['params']
        return params[key_val]

    taxi_type = get_param('taxi_type')
    years = get_param('years')
    months = get_param('months')
    tgt_schema = get_param('tgt_schema')

    # Get list of URLs to pull
    url_list = pull_taxi_data(
        taxi_type, 
        years, 
        months
    )

    # Write URLs to bucket
    urls_written = write_data_to_postgres(
        url_list=url_list,
        taxi_type=taxi_type,
        tgt_schema=tgt_schema
    )

    [taxi_type, years, months, tgt_schema] >> url_list >> urls_written