from minio import Minio

client = Minio("IP:PORT",
    access_key="username",
    secret_key="pwd", secure=False
)
bucket_name = "humaine"
found = client.bucket_exists(bucket_name)
if not found:
    client.make_bucket(bucket_name)
    print("Created bucket", bucket_name)
else:
    print("Bucket", bucket_name, "already exists")


source_file= resultPredictions.png
destination_file=resultPredictions.png
metadata={'key':'value'}
client.fput_object(
    bucket_name, destination_file, source_file, metadata=metadata
)
print(
    source_file, "successfully uploaded as object",
    destination_file, "to bucket", bucket_name,
)
