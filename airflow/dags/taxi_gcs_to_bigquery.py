import os
import sys
from airflow import DAG
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.decorators import task
from airflow.models.param import Param
from datetime import datetime
from tasks.taxi_tasks import (
    write_gcs_to_bigquery
)

with DAG(
    dag_id='taxi_gcs_to_bigquery',
    start_date=datetime(2024, 1, 1),
    schedule=None, # '@daily', # Optional daily schedule
    catchup=False,
    params={
        'months': Param(default=['01', '02', '03', '04', '05', '06', '07', '08', '09',
                                '10', '11', '12']), # Months to pull data for
        'years': Param(default=['2022']), # Years to pull data for
        'taxi_type': Param(default='green'), # Taxi type to pull data for
        'tgt_bucket_name': Param(default='green-taxi-data'), # Suffix to add to project for bucket name
        'force_overwrite': Param(default=False), # Overwrite all data - ignore checks on existence
        'tgt_bigquery_dataset': Param(default='ny_taxi_raw')
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
    tgt_bigquery_dataset = get_param('tgt_bigquery_dataset')

    # Trigger the GCS write
    trigger_gcs_write = TriggerDagRunOperator(
        task_id="trigger_gcs_dag",
        trigger_dag_id="taxi_data_to_gcs",
        wait_for_completion=True,
        conf={ # Pass params to GCS DAG
            'taxi_type': taxi_type,
            'years': years,
            'months': months,
            'tgt_bucket_name': tgt_bucket_name,
            'force_overwrite': force_overwrite
        }
    )

    # Write data to BigQuery
    bigquery_written = write_gcs_to_bigquery(
        tgt_dataset=tgt_bigquery_dataset,
        years=years,
        bucket_suffix=tgt_bucket_name,
        taxi_type=taxi_type,
        input_data_type='PARQUET'
    )

    # Define sequencing
    [taxi_type, years, months, force_overwrite, tgt_bigquery_dataset] >> \
        trigger_gcs_write >> bigquery_written