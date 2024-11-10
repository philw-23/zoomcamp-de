import os
import sys
from airflow import DAG
from datetime import datetime
from tasks.taxi_tasks import (
    pull_taxi_data,
    validate_bucket,
    write_urls_to_bucket
)

# Set default params for DAG
default_params={
    'months': ['01', '02', '03', '04', '05', '06', '07', '08', '09',
                '10', '11', '12'],
    'years': ['2019'],
    'taxi_type': 'green'
}

with DAG(
    dag_id='taxi_data_to_gcs',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
    params=default_params,
    tags=['data-zoomcamp']
) as dag:
    
    # GCP variables
    GCP_PROJECT = os.environ.get('GCP_PROJECT_ID')
    GCS_LOCATION = os.environ.get('GCP_LOCATION')
    BUCKET_NAME = GCP_PROJECT + '-' + dag.params['taxi_type'] + '-bucket-2019'

    # Validate bucket and get folders
    bucket_folders = validate_bucket(
        project_id=GCP_PROJECT,
        bucket_name=BUCKET_NAME,
        gcs_location=GCS_LOCATION
    )

    # Get list of URLs to pull
    url_list = pull_taxi_data(
        dag.params['taxi_type'], 
        dag.params['years'], 
        dag.params['months']
    )

    # Write URLs to bucket
    urls_written = write_urls_to_bucket(
        url_list=url_list,
        project_id=GCP_PROJECT,
        bucket_name=BUCKET_NAME,
        bucket_folders=bucket_folders
    )

    # Sequence events
    bucket_folders >> url_list >> urls_written