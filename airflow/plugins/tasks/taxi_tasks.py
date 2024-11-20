import os
from airflow.decorators import task

'''
    Function to pull taxi data for a specific taxi type (yellow, green, fhv, fhvhv)
    from the nyc taxi website.
        taxi_type: green, yellow, fhv
        years: list of years (as string) to pull data for
        months: list of months (as string, "00" format) to pull data for
'''
@task
def pull_taxi_data(taxi_type, years, months):
    # Pull required imports - placing in here to only load when needed
    from bs4 import BeautifulSoup
    import requests
    import re

    # Pull url request
    resp = requests.get('https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page') # data page
    soup = BeautifulSoup(resp.text, 'lxml') # Parse URL results
    urls = soup.find_all('a', href=True) # Get all URLs through anchors

    # Month string for regex (same for all years)
    month_string = "|.*-".join(months) # Create a string for months, | is or in regex
    
    # Iterate over all years
    url_dict = {} # Dictionary for storing results by year
    for year in years:
        # Build regex
        # (?=.*-{month_string}) looks for a match on month preceeded by dash
        # (?=.*{year_string}) looks for a match on year preceeded by underscore
        # (?=.*{taxi_type}) looks for a match on taxi type
        # .*parquet$ looks for "ends with .parquet"
        full_string = (
            f"(?=.*-{month_string})(?=.*_{year})(?=.*{taxi_type}_).*parquet$"
        )
        rgx = re.compile(full_string) # Compile regex

        # Get list of URLs
        download_urls = []
        for check_url in urls: # Iterate over everything
            url = check_url['href'].strip() # Get URL from href
            if re.match(rgx, url): # Check for a match
                download_urls.append(url)

        # Add to dictionary
        url_dict[year] = download_urls

        # Print matches
        print(f'For {year} - matched {len(download_urls)} URLs')

    # Return URL list
    return url_dict

'''
    Function to validate the existence of GCS bucket and create if not. Assumes
    that required gcp credentials are exported
        project_id: gcp project id where bucket will live
        bucket_name: name of bucket to be created
        gcs_location: location for bucket to be created in
        storage_class: storage class to use for bucket
'''
@task
def validate_bucket(project_id, bucket_name, gcs_location, storage_class='STANDARD'):
    # Import required packages
    from google.cloud import storage

    # Initiate Client
    client = storage.Client(project_id)

    # Create bucket object
    bucket = client.bucket(bucket_name)
    bucket.location = gcs_location
    bucket.storage_class = storage_class

    if bucket.exists(): # If it exists - check for directory files that exist
        print(f'Bucket {bucket_name} already exists - getting existing folders!')
        blobs = bucket.list_blobs() # Get list of blobs
        bucket_folders = [] # For appending prefixes
        for blob in blobs:
            folder_path = blob.name.rsplit('/', 1)[0] # Splits off last piece
            bucket_folders.append(folder_path)

        # Drop duplicates!
        bucket_folders = list(set(bucket_folders))

    else:
        bucket = client.create_bucket(bucket_name)
        print(f'Bucket {bucket_name} successfully created!')
        bucket_folders = [] # List of folders that exist in bucket (for checking on writes)

    # Return existing folders
    return bucket_folders

'''
    Function to write data URLs to GCS bucket
        url_list: list of URLs to write
        project_id: project where bucket lives
        bucket_name: bucket to write the data to
        bucket_folders: list of existing bucket folders to check before writing
        force_overwrite: overwrite all data, ignore checks on existence
'''
@task
def write_urls_to_bucket(url_list, project_id, bucket_name, bucket_folders, force_overwrite):
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
    for year, url_vals in url_list.items():
        print(f'Writing data for year {year}')

        # Iterate over all years
        for url in url_vals:
            # Declare start
            start_time = time.time()
            print(f'Writing {url} to GCS bucket')

            # Create base table name
            table_name = url.split('/')[-1] # Extract table name from end of url
            table_name = table_name.replace('.parquet', '') # Replace as we are writing in chunks
            folder_path = year + '/' + table_name # For checking existence

            # Check if we already have table in GCS
            # Check if we already have folder and are not force overwriting
            if folder_path in bucket_folders and not force_overwrite:
                print(f'Data bucket {folder_path} for URL already exists - skipping')
                continue

            # Get the file and write in mem
            file_pull = requests.get(url)
            file_pull.raise_for_status() # Ensure success
            parquet_data = BytesIO(file_pull.content) # In mem read
            parquet_file = pq.ParquetFile(parquet_data) # Get parquet table

            # Iterate over chunks
            batches = parquet_file.iter_batches(batch_size=chunk_size)
            for idx, chunk in enumerate(batches):
                print(f'Writing chunk {str(idx)} of URL')
                chunk.to_pandas().to_parquet('./tmp_chunk.parquet') # Write to local file
                blob_name = f'{year}/{table_name}/chunk_{str(idx)}.parquet' # chunk name for write
                blob = bucket.blob(blob_name) # Define blob for upload
                blob.upload_from_filename('./tmp_chunk.parquet') # Upload blob from filename

            # Print success
            run_time = round(time.time() - start_time, 2)
            print(f'Successfully wrote {url} to GCS bucket in {run_time}s')

    # Fully complete
    if os.path.exists('./tmp_chunk.parquet'):
        os.remove('./tmp_chunk.parquet') # Remove file
    print('All URLs sucessfully written')

'''
    Function to write data URLs to postgres datawarehouse
        url_list: list of URLs to download and write to postgres
        taxi_type: taxi type for data write (will be part of table name for data)
        tgt_schema: target schema to write the data to
'''
@task
def write_data_to_postgres(url_list, taxi_type, tgt_schema):
    import time
    import requests
    import pandas as pd
    import pyarrow.parquet as pq
    from io import BytesIO
    from concurrent.futures import ThreadPoolExecutor
    from sqlalchemy import create_engine, inspect
    from sqlalchemy.engine import URL
    from sqlalchemy.schema import CreateSchema

    # Set chunk size for parquet iterating
    chunk_size= 4 * 65536 # Number of rows to iterate

    # Create postgres engine
    # NOTE: broad pg permissions are bad practice in production
    # Would want to create airflow specific account with desired roles
    pg_url = URL.create(
        drivername='postgresql',
        username=os.environ.get('PG_DWH_USER'),
        password=os.environ.get('PG_DWH_PASSWORD'),
        host=os.environ.get('PG_DWH_HOST'),
        port=5432, # Use 5432 since we are within the container
        database=os.environ.get('PG_DWH_DBNAME')
    )
    pg_engine = create_engine(pg_url)
    pg_inspect = inspect(pg_engine) # Create inspector for checks

    # Create target schema if it doesn't exist
    if tgt_schema not in pg_inspect.get_schema_names(): # Check for schema existence
        print(f'Schema {tgt_schema} does not exist in database - creating')
        with pg_engine.connect() as conn:
                with conn.begin(): # Execute
                    conn.execute(CreateSchema(tgt_schema, if_not_exists=True))

    # Creates generator for data chunks
    # TODO: factor this to it's own function
    def generate_data_chunks(url_lists, chunk_size):
        for year, url_vals in url_list.items():
            # print(f'Writing data for year {year}')
            # Create table name
            table_name = f'{taxi_type}_data_{year}' # Combine taxi type and year

            # Check for table existence - truncate if so
            if table_name in pg_inspect.get_table_names(schema=tgt_schema):
                print(f'Table {tgt_schema}.{table_name} already exists - truncating data')
                with pg_engine.connect() as conn:
                    conn.execute(f'TRUNCATE TABLE {tgt_schema}.{table_name}')

            # Iterate over all years
            for url in url_vals:
                # Declare start
                start_time = time.time()
                # print(f'Writing {url} to Postgres')

                # Get the file and write in mem
                file_pull = requests.get(url)
                file_pull.raise_for_status() # Ensure success
                parquet_data = BytesIO(file_pull.content) # In mem read
                parquet_file = pq.ParquetFile(parquet_data) # Get parquet table

                # Iterate over chunks
                batches = parquet_file.iter_batches(batch_size=chunk_size)
                for idx, batch in enumerate(batches):
                    yield idx, batch, url, year, table_name

    # Writes generator batch to postgres
    def write_batch_to_postgres(inputs):
        # Get inputs
        idx, batch, url, year, table_name = inputs

        print(f'For year {year}: writing chunk {idx} of {url} to {table_name}')
        pd_chunk = batch.to_pandas() # Convert to pandas
        
        # Write data - append if table exists
        with pg_engine.connect() as pg_conn:
            pd_chunk.to_sql(
                name=table_name,
                con=pg_conn,
                schema=tgt_schema,
                if_exists='append',
                index=False
            )

    # Multiprocess - no workers specified
    with ThreadPoolExecutor() as executor:
        # Takes in function, and iterables
        executor.map(
            write_batch_to_postgres, 
            generate_data_chunks(url_list, chunk_size=chunk_size)
        )

    # # Iterate over all URLs as write to fs
    # for year, url_vals in url_list.items():
    #     print(f'Writing data for year {year}')

    #     # Create table name
    #     table_name = f'{taxi_type}_data_{year}' # Combine taxi type and year

    #     # Check for table existence - truncate if so
    #     if table_name in pg_inspect.get_table_names(schema=tgt_schema):
    #         print(f'Table {tgt_schema}.{table_name} already exists - truncating data')
    #         with pg_engine.connect() as conn:
    #             conn.execute(f'TRUNCATE TABLE {tgt_schema}.{table_name}')

    #     # Iterate over all years
    #     for url in url_vals:
    #         # Declare start
    #         start_time = time.time()
    #         print(f'Writing {url} to Postgres')

    #         # Get the file and write in mem
    #         file_pull = requests.get(url)
    #         file_pull.raise_for_status() # Ensure success
    #         parquet_data = BytesIO(file_pull.content) # In mem read
    #         parquet_file = pq.ParquetFile(parquet_data) # Get parquet table

    #         # Iterate over chunks
    #         batches = parquet_file.iter_batches(batch_size=chunk_size)
    #         with pg_engine.connect() as pg_conn: # Connect to engine
    #             for idx, chunk in enumerate(batches):
    #                 print(f'Writing chunk {str(idx)} of URL')
    #                 pd_chunk = chunk.to_pandas() # Convert to pandas
                    
    #                 # Write data - append if table exists
    #                 pd_chunk.to_sql(
    #                     name=table_name,
    #                     con=pg_conn,
    #                     schema=tgt_schema,
    #                     if_exists='append',
    #                     index=False
    #                 )

    #         # Print success
    #         run_time = round(time.time() - start_time, 2)
    #         print(f'Successfully wrote {url} to Postgres in {run_time}s')

    # Fully complete
    print('All URLs sucessfully written')

    # Dispose of engine
    pg_engine.dispose()