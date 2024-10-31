import pyarrow as pa 
import pyarrow.parquet as pq
import os

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

# Generate bucket variables
bucket_name = f'{project_id}-yellowtaxi-bucket' # Bucket name to use
table_name = 'nyc_taxi_data' # What we will name our parquet table (pyarrow will partition)
root_path = f'{bucket_name}/{table_name}' # Path where pyarrow will write the data

@data_exporter
def export_data(data, *args, **kwargs):
    # Add date column to partition on!
    data['tpep_pickup_date'] = data['tpep_pickup_datetime'].dt.date

    # Define a pyarrow table for data
    table = pa.Table.from_pandas(data) # Convert pandas df from previous step

    # Set filesystem - uses environment variable
    gcs = pa.fs.GcsFileSystem() 

    # Write dataset!
    pq.write_to_dataset(
        table=table, # Table to write
        root_path=root_path, # Root path to write data to
        partition_cols=['tpep_pickup_date'], # Columns to partition the data on
        filesystem=gcs # Filesystem to use for writing
    )

