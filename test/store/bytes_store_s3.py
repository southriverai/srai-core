import os

import requests

from srai_core.store.bytes_store_s3 import BytesStoreS3
from srai_core.tools_env import get_string_from_env
from srai_core.tools_s3 import bucket_create_read_only, bucket_exists, create_client_and_resource_s3

aws_access_key_id = get_string_from_env("AWS_ACCESS_KEY_ID")
aws_secret_access_key = get_string_from_env("AWS_SECRET_ACCESS_KEY")
aws_name_region = get_string_from_env("AWS_REGION_NAME")
bucket_name = "srai-generated-videos"
client_s3, resource_s3 = create_client_and_resource_s3(aws_access_key_id, aws_secret_access_key, aws_name_region)


if not bucket_exists(client_s3, resource_s3, bucket_name):
    print("Bucket does not exist, creating")
    bucket_create_read_only(client_s3, resource_s3, bucket_name, aws_name_region)
else:
    print("Bucket exists")


store = BytesStoreS3(aws_access_key_id, aws_secret_access_key, aws_name_region, bucket_name)
test_id = "test_id"

with open(os.path.join("test", "data", "test.txt"), "rb") as file:
    test_data = file.read()

if store.exists_bytes(test_id):
    print("Deleting existing test data")
    store.delete_bytes(test_id)
print("Saving test data")
store.save_bytes(test_id, test_data)
if not store.exists_bytes(test_id):
    raise Exception("Failed to save test data")
else:
    print("Test data saved successfully")
# store.delete_bytes(test_id)
print(store.get_bytes_url(test_id))

response = requests.get(store.get_bytes_url(test_id))
print(response.content)

# write new object to public bucket using requests
response = requests.put(store.get_bytes_url("test_id"), data=b"test data")
print(response.content)
