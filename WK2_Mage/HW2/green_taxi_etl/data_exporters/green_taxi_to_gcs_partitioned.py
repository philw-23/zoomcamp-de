import pyarrow as pa 
import pyarrow.parquet as pq
import os
from mage_zoomcamp.utils.shared import validate_bucket

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

# Get needed env variables
project_id = os.getenv('GCP_PROJECT') # Project
region = os.getenv('GCS_LOCATION') # Region
key_path = os.getenv('KEY_DEST') # Key location

# NOTE: GCS filesystem in pyarrow effectively requires GOOGLE_APPLICATION_CREDENTIALS
#       env variable to be set. See documentation: 
#       https://arrow.apache.org/docs/python/generated/pyarrow.fs.GcsFileSystem.html#pyarrow.fs.GcsFileSystem
# We can set this as shown below
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path

@data_exporter
def export_data(data, *args, **kwargs):
    # Generate bucket variables
    bucket_suffix = kwargs['bucket_suffix'] # Bucket suffix
    bucket_table_name = kwargs['bucket_table_name']
    bucket_name = f'{project_id}-{bucket_suffix}' # Bucket name to use

    # Validate bucket
    validate_bucket(
        project_id=project_id,
        bucket_name=bucket_name,
        gcs_location=region,
        key_path=key_path
    )

    # Define a pyarrow table for data
    table = pa.Table.from_pandas(data) # Convert pandas df from previous step

    # Set filesystem - uses environment variable
    gcs = pa.fs.GcsFileSystem() 

    # Define path for bucket write
    root_path = f'{bucket_name}/{bucket_table_name}' # Path where pyarrow will write the data

    # Write dataset!
    pq.write_to_dataset(
        table=table, # Table to write
        root_path=root_path, # Root path to write data to
        partition_cols=['lpep_pickup_date'], # Columns to partition the data on
        filesystem=gcs # Filesystem to use for writing
    )

    # Confirm data write
    print('Data successfully written to GCS!')

