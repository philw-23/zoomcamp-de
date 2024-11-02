from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.google_cloud_storage import GoogleCloudStorage
from mage_zoomcamp.utils.shared import validate_bigquery
from os import path, getenv

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test



@data_loader
def load_from_google_cloud_storage(*args, **kwargs):
    """
    Template for loading data from a Google Cloud Storage bucket.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#googlecloudstorage
    """
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'

    # Get environment variables
    project_id = getenv('GCP_PROJECT')
    location = getenv('GCS_LOCATION')
    key_path = getenv('KEY_DEST')

    # Get name for bigquery dataset (effectively schema)
    # Note: using pipeline variable here! Access as shown below
    bq_dataset_name = kwargs['bq_dataset_name']

    # Validate if bigquery dataset exists!
    validate_bigquery(
        project_id=project_id,
        dataset_name=bq_dataset_name,
        dataset_loc=location,
        key_path=key_path
    )

    # GCS Bucket variables to read data from
    bucket_name = f'{project_id}-yellowtaxi-bucket' # Bucket name to use
    object_key = 'nyc_taxi_data.parquet' # Filename to use in the bucket

    return GoogleCloudStorage.with_config(ConfigFileLoader(config_path, config_profile)).load(
        bucket_name,
        object_key,
    )


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
