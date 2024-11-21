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
        'force_overwrite': Param(default=False) # Overwrite all data - ignore checks on existence
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
    force_overwrite = get_param('force_overwrite')

    # GCP variables
    GCP_PROJECT = os.environ.get('GCP_PROJECT_ID')
    GCS_LOCATION = os.environ.get('GCP_LOCATION')
    BUCKET_BASE = GCP_PROJECT + '-taxi-data'

    # Validate bucket and get folders
    bucket_folders = validate_bucket(
        project_id=GCP_PROJECT,
        bucket_base=BUCKET_BASE,
        gcs_location=GCS_LOCATION,
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
        project_id=GCP_PROJECT,
        bucket_base=BUCKET_BASE,
        bucket_folders=bucket_folders,
        force_overwrite=force_overwrite,
        taxi_type=taxi_type
    )

    [taxi_type, years, months, force_overwrite] >> bucket_folders >> \
        url_list >> urls_written