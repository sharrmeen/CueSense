from minio import Minio
import os

BUCKET_A_ROLL = "a-roll"
BUCKET_B_ROLL = "b-roll"
BUCKET_OUTPUTS="output"

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Ensure buckets exist on startup
for bucket in [BUCKET_A_ROLL, BUCKET_B_ROLL,BUCKET_OUTPUTS]:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)