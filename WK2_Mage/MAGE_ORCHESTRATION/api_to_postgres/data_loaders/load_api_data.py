# Imports needed packages
import io
import pandas as pd
import requests

# Ensures mage has the required decorators loaded
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


# This is the data loader object
# It will return the dataframe from the compressed API source
@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
    """
    # Compressed URL for 2021-01 yellow taxi data
    url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz' 

    # Declare datatypes - reduces the memory usage pandas uses while processing data
    # Generally these can be found by exploring a small subset of the data
    # Pipeline will fail if we see different datatypes - which is good! We know we need to update
    taxi_dtypes = {
        'VendorID': pd.Int64Dtype(),
        'passenger_count': pd.Int64Dtype(),
        'trip_distance': float,
        'RatecodeID': pd.Int64Dtype(),
        'store_and_fwd_flag': str,
        'PULocationID': pd.Int64Dtype(),
        'DOLocationID': pd.Int64Dtype(),
        'fare_amount': float,
        'extra': float,
        'mta_tax': float,
        'tip_amount': float,
        'tolls_amount': float,
        'improvement_surcharge': float,
        'total_amount': float,
        'congestion_surcharge': float
    }

    # Note: we did not specify dtypes for these datetime columns
    # This is because we can use the parse_dates argument in read_csv so pandas will do this for us
    parse_dates = ['tpep_pickup_datetime', 'tpep_dropoff_datetime']

    # Can use read_csv on the direct URL
    # Specify the separator, compression type, dtypes we defined, and parse 
    # Note that when we connect a transormation block to this block - this will serve as the input
    return pd.read_csv(url, sep=',', compression='gzip', dtype=taxi_dtypes, parse_dates=parse_dates)

# Test decorators will run tests to ensure our data loader is working properly
@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
