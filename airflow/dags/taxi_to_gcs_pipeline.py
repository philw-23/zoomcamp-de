import os
import sys
from airflow import DAG
from airflow.decorators import task
from airflow.models.param import Param
from datetime import datetime
from tasks.taxi_tasks import (
    pull_taxi_data,
    validate_bucket,
    write_urls_to_bucket
)

with DAG(
    dag_id='taxi_data_to_gcs',
    start_date=datetime(2024, 1, 1),
    schedule=None, # '@daily', # Optional daily schedule
    catchup=False,
    params={
        'months': Param(default=['01', '02', '03', '04', '05', '06', '07', '08', '09',
                                '10', '11', '12']), # Months to pull data for
        'years': Param(default=['2022']), # Years to pull data for
        'taxi_type': Param(default='green'), # Taxi type to pull data for
        'tgt_bucket_name': Param(default='green-taxi-data'), # Suffix to add to project for bucket name
        'force_overwrite': Param(default=False) # Overwrite all data - ignore checks on existence
    },
    tags=['data-zoomcamp']
) as dag:
    
    # NOTE
    # All bucket names used for gcp are of the format: project-bucket_suffix!

    # Get runtime parameters
    @task
    def get_param(key_val, **kwargs):
        params = kwargs['params']
        return params[key_val]

    taxi_type = get_param('taxi_type')
    years = get_param('years')
    months = get_param('months')
    tgt_bucket_name = get_param('tgt_bucket_name')
    force_overwrite = get_param('force_overwrite')

    # Validate bucket and get folders
    bucket_folders = validate_bucket(
        bucket_suffix=tgt_bucket_name,
        taxi_type=taxi_type
    )

    # Get list of URLs to pull
    url_list = pull_taxi_data(
        taxi_type,
        years,
        months
    )

    # Write URLs to bucket
    urls_written = write_urls_to_bucket(
        url_list=url_list,
        bucket_suffix=tgt_bucket_name,
        bucket_folders=bucket_folders,
        force_overwrite=force_overwrite,
        taxi_type=taxi_type
    )

    # Define sequencing
    [taxi_type, years, months, force_overwrite] >> bucket_folders >> \
        url_list >> urls_written