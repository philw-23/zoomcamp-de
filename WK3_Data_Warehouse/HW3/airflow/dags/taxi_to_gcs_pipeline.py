import os
from datetime import datetime
from airflow import DAG
from airflow.decorators import task

'''
    Function to pull taxi data for a specific taxi type (yellow, green, fhv, fhvhv)
    from the nyc taxi website.
        taxi_type: green, yellow, fhv
        years: list of years (as string) to pull data for
        months: list of months (as string, "00" format) to pull data for
'''
def pull_taxi_data(taxi_type, years, months):
    # Pull required imports - placing in here to only load when needed
    from bs4 import BeautifulSoup
    import requests
    import re

    # Pull url request
    resp = requests.get('https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page') # data page
    soup = BeautifulSoup(resp.text, 'lxml') # Parse URL results
    urls = soup.find_all('a', href=True) # Get all URLs through anchors

    # Create re search object
    month_string = "|.*-".join(months) # Create a string for months, | is or in regex
    year_string = "|.*_".join(years) # Create a string for years, | is or in regex
    # Build regex
    # (?=.*-{month_string}) looks for a match on month preceeded by dash
    # (?=.*{year_string}) looks for a match on year preceeded by underscore
    # (?=.*{taxi_type}) looks for a match on taxi type
    # .*parquet$ looks for "ends with .parquet"
    full_string = (
        f"(?=.*-{month_string})(?=.*_{year_string})(?=.*{taxi_type}).*parquet$"
    )
    rgx = re.compile(full_string) # Compile regex

    # Get list of URLs
    download_urls = []
    for check_url in urls: # Iterate over everything
        url = check_url['href'].strip() # Get URL from href
        if re.match(rgx, url): # Check for a match
            download_urls.append(url)

    # Print matches
    print(f'Matched {len(download_urls)} URLs')
    print(f'URL List: {download_urls}')

    # Return URL list
    return download_urls

'''
    Function to validate the existence of GCS bucket and create if not. Assumes
    that required gcp credentials are exported
        project_id: gcp project id where bucket will live
        bucket_name: name of bucket to be created
        gcs_location: location for bucket to be created in
        storage_class: storage class to use for bucket
'''
def validate_bucket(project_id, bucket_name, gcs_location, storage_class='STANDARD'):
    # Import required packages
    from google.cloud import storage

    # Initiate Client
    client = storage.Client(project_id)

    # Create bucket object
    bucket = client.bucket(bucket_name)
    bucket.location = gcs_location
    bucket.storage_class = storage_class

    if bucket.exists(): # If it exists - do nothing
        print(f'Bucket {bucket_name} already exists - no action taken!')
    else:
        bucket = client.create_bucket(bucket_name)
        print(f'Bucket {bucket_name} successfully created!')

'''
    Function to write data URLs to GCS bucket
        url_list: list of URLs to write
        project_id: project where bucket lives
        bucket_name: bucket to write the data to
'''
def write_urls_to_bucket(url_list, project_id, bucket_name):
    # Import required packages
    import time
    import requests
    import pandas as pd
    import pyarrow.parquet as pq
    from google.cloud import storage
    from io import BytesIO

    # Initialize client
    client = storage.Client()

    # Initialize bucket
    bucket = client.bucket(bucket_name)

    # Set chunk size for iterating
    chunk_size= 8 * 65536 # Number of rows to iterate
    
    # Set start time

    # Iterate over all URLs as write to fs
    for url in url_list:
        # Declare start
        start_time = time.time()
        print(f'Writing {url} to GCS bucket')

        # Get the file and write in mem
        file_pull = requests.get(url)
        file_pull.raise_for_status() # Ensure success
        parquet_data = BytesIO(file_pull.content) # In mem read
        parquet_file = pq.ParquetFile(parquet_data) # Get parquet table

        # Create base table name
        table_name = url.split('/')[-1] # Extract table name from end of url
        table_name = table_name.replace('.parquet', '') # Replace as we are writing in chunks

        # Iterate over chunks
        batches = parquet_file.iter_batches(batch_size=chunk_size)
        for idx, chunk in enumerate(batches):
            print(f'Writing chunk {str(idx)} of URL')
            chunk.to_pandas().to_parquet('./tmp_chunk.parquet') # Write to local file
            blob_name = f'{table_name}/chunk_{str(idx)}.parquet' # chunk name for write
            blob = bucket.blob(blob_name) # Define blob for upload
            blob.upload_from_filename('./tmp_chunk.parquet') # Upload blob from filename

        # Print success
        run_time = round(time.time() - start_time, 2)
        print(f'Successfully wrote {url} to GCS bucket in {run_time}s')

    # Fully complete
    os.remove('./tmp_chunk.parquet') # Remove file
    print('All URLs sucessfully written')

########################################################################
# RUNS
########################################################################
# Define data variables
months = [
    '01', '02', '03', '04', '05', '06', '07', '08', '09',
    '10', '11', '12'
]
taxi_type = 'yellow'
years = ['2019']

# GCP variables
GCP_PROJECT = os.environ.get('GCP_PROJECT_ID')
GCS_LOCATION = os.environ.get('GCP_LOCATION')
BUCKET_NAME = GCP_PROJECT + '-' + taxi_type + '-bucket-2019'

# Run functions (will convert this to DAG afterwards)
url_list = pull_taxi_data(taxi_type, years, months)
validate_bucket(
    project_id=GCP_PROJECT,
    bucket_name=BUCKET_NAME,
    gcs_location=GCS_LOCATION
)
write_urls_to_bucket(
    url_list=url_list,
    project_id=GCP_PROJECT,
    bucket_name=BUCKET_NAME
)