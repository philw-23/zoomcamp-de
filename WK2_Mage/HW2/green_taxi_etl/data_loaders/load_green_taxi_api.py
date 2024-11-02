import io
import pandas as pd

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


'''
    Define a function to format url for data download from the following location
    based on year and month provided
    LOCATION: https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/green/download
        year: year of data
        month: month of data
'''
def create_data_url(year, month):
    # Convert input variables if needed!
    if type(year) != str:
        year = str(year) # Convert input to string
    if int(month) < 10:
        month = '0' + str(month) # Format to two digits
    else:
        month = str(month) # Convert to string

    # Note the download URL is different than the location URL!
    base_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/'
    data_url = f'green_tripdata_{year}-{month}.csv.gz'

    return base_url + data_url

@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
    """
    # Get variables for pulling specific months and years
    years = kwargs['years']
    months = kwargs['months']

    # Check to verify inputs are correct
    assert type(years) == list, 'Years not provided as list of integers'
    assert type(months) == list, \
        'Months not provided as list of integers, single digit months must be passed as one digit'

    # Specify taxi dtypes to use for load
    # We are using the same dtypes as from our yellow taxi pipeline
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

    # Specify dates to parse
    # Note: date columns are "lpep" and not "tpep"!
    parse_dates = ['lpep_pickup_datetime', 'lpep_dropoff_datetime']

    # Iterate over all combos and store results
    url_results = [] # For storing results
    for year in years: # Iterate through years
        for month in months: # Iterate through months
            url = create_data_url(year, month) # Create URL
            df = pd.read_csv( # Read URL
                url, 
                sep=',', 
                compression='gzip',
                dtype=taxi_dtypes, 
                parse_dates=parse_dates
            )
            url_results.append(df) # Append intermediate results

    # Concatentate individual DFs
    data = pd.concat(url_results)
    print(f'Data of shape {data.shape} successfully downloaded') # Get shape of loaded data

    # Return data
    return data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
