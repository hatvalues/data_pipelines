from google.cloud.storage import Client as StorageClient
from google.cloud.bigquery import Client as BigQueryClient
from google.api_core.exceptions import Conflict
from google.cloud.bigquery import SourceFormat, LoadJobConfig, WriteDisposition
from decouple import config
import pyarrow as pa
import pyarrow.parquet as pq
from anal_pipe.environment import set_google_crendentials
set_google_crendentials()

gcp_projet_id = config("PROJECT_ID")
dataset = config("DATASET")

# Set up the client objects
bq_client = BigQueryClient()
job_config = LoadJobConfig(
    autodetect=True, source_format=SourceFormat.PARQUET,
    write_disposition=WriteDisposition.WRITE_EMPTY
)

storage_client = StorageClient()
bucket_name = config("BUCKET_NAME", default='default-bk')
bucket = storage_client.bucket(bucket_name)

for blob in bucket.list_blobs(prefix='synth_parquet_files/'):
    # control the PIO cost, use the small file in dev
    print(blob.name)
    if 'small' in blob.name:
        source_uri = f'gs://{bucket_name}/{blob.name}'
        # Load the data into BigQuery
        table_id = f'{gcp_projet_id}.{dataset}.small_synth_parq'
        job = bq_client.load_table_from_uri(
            source_uri, table_id, job_config=job_config
        )
        # Wait for the job to complete
        try:
            job.result()
            print(job.state)
            print(job.started, job.ended)
        except Conflict:
            print(f'{table_id} already exists. Aborting')
# Check for errors
# if load_job.errors:
#     for error in load_job.errors:
#         print(error["message"])
# else:
#     print("Data loaded successfully.")
