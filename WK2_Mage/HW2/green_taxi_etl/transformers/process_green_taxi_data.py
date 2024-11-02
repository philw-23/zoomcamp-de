if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


'''
    Function to remove rows where passenger count and trip distance equal 0
        data: input dataframe
'''
def remove_missing_values(data):
    # Get initial length of dataframe
    init_len = len(data) 

    # Remove items
    data = data.loc[
        ~(data['trip_distance'] == 0) & # Trip distance != 0
        ~(data['passenger_count'] == 0) # Passenger count != 0
    ]

    # Get new df length
    final_len = len(data)

    # Print results
    print('Removing Rows w/ passenger_count = 0 and trip_distance = 0')
    print(f'Removed {init_len - final_len} rows')
    print(f'New data size: {data.shape}')

    # Return data
    return data


@transformer
def transform(data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Convert lpep_pickup_data
    data['lpep_pickup_date'] = data['lpep_pickup_datetime'].dt.date

    # Record original columns
    original_columns = data.columns # For change comparison
    print('Changing columns to camel case')

    # Convert to camel case
    data.columns = (
        data.columns.str.replace(r'(?<!^)(?=[A-Z][a-z])', '_', regex=True) # Case for uppercase then lowercase
                .str.replace(r'(?<=[a-z])(?=[A-Z])', '_', regex=True) # Multiple upper case consecutively
                .str.lower() # Convert to lower case
                .str.replace(r'\_{2,}', '_', regex=True) # Replace more than 2 underscores with 1
    )

    # Validate how many have changed
    changes = len(data.columns) - sum(data.columns == original_columns)
    print(f'Changed {changes} columns to camel case')

    # Specify your transformation logic here
    data = remove_missing_values(data)

    # Print unique vendor values
    vendor_values = data['vendor_id'].unique().tolist()
    print(f'Unique vendor values in dataset: {vendor_values}')

    # Return data
    return data


@test
def test_vendor_id(output, *args) -> None:
    # NOTE: assuming test assumes there are no null vendor values
    assert len(output.loc[output['vendor_id'].isnull()]) == 0, \
        'Undefined vendor values present!'

@test
def test_passenger_count(output, *args) -> None:
    # Test there are no zero passenger counts
    assert len(output.loc[output['passenger_count'] == 0]) == 0, \
        'Rows with zero passengers present!'

@test
def test_trip_distance(output, *args) -> None:
    # Test there are no zero passenger counts
    assert len(output.loc[output['trip_distance'] == 0]) == 0, \
        'Rows with no trip distance present!'