# Loads tranformer decorators if needed
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform_zero(data, *args, **kwargs):
    # Print out how many rows have no passengers
    print(f'''Rows with zero passengers: {len(data.loc[data['passenger_count'] == 0])}''')

    # Remove data with no passengers via return
    return data.loc[data['passenger_count'] > 0]


# Test whether zero passenger rides were removed
@test
def test_zero(output, *args) -> None:
    assert len(output.loc[output['passenger_count'] == 0]) == 0, \
        'Rides exist with 0 passengers!'