from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.google_cloud_storage import GoogleCloudStorage
from pandas import DataFrame
from os import path, getenv

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_google_cloud_storage(df: DataFrame, **kwargs) -> None:
    """
    Template for exporting data to a Google Cloud Storage bucket.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#googlecloudstorage
    """
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default' # Config profile where credentials are saved!

    # Get environment variables
    project_id = getenv('GCP_PROJECT')
    region = getenv('GCS_LOCATION')
    key_path = getenv('KEY_DEST')

    # Generate bucket variables
    bucket_name = f'{project_id}-yellowtaxi-bucket' # Bucket name to use
    object_key = 'nyc_taxi_data.parquet' # Filename to use in the bucket

    # Write data to single file in GCS bucket
    # Note this will not partition the data - this is documented in the 
    GoogleCloudStorage.with_config(ConfigFileLoader(config_path, config_profile)).export(
        df,
        bucket_name,
        object_key,
    )
