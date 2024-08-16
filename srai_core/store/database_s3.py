from srai_core.store.bytes_store_base import BytesStoreBase
from srai_core.store.bytes_store_s3 import BytesStoreS3
from srai_core.store.database_base import DatabaseBase
from srai_core.store.document_store_base import DocumentStoreBase
from srai_core.tools_s3 import bucket_list, create_client_and_resource_s3


class DatabaseS3(DatabaseBase):
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_name_region: str,
        create_bucket_if_missing: bool = True,
    ):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_name_region = aws_name_region
        self.create_bucket_if_missing = create_bucket_if_missing

    def list_collection_names(self) -> list[str]:
        client_s3, resource_s3 = create_client_and_resource_s3(
            self.aws_access_key_id, self.aws_secret_access_key, self.aws_name_region
        )
        return bucket_list(client_s3, resource_s3)

    def get_document_store(self, collection_name: str) -> DocumentStoreBase:
        raise NotImplementedError("Document store is not supported for S3 databases")

    def get_bytes_store(self, collection_name: str) -> BytesStoreBase:
        return BytesStoreS3(
            self.aws_access_key_id,
            self.aws_secret_access_key,
            self.aws_name_region,
            collection_name,
            create_bucket_if_missing=self.create_bucket_if_missing,
        )
