from base64 import b64decode, b64encode
from typing import Dict

from srai_core.store.bytes_store_base import BytesStoreBase
from srai_core.store.document_store_mongo import DocumentStoreMongo


class BytesStoreMongo(BytesStoreBase):

    def __init__(self, connection_string: str, database_name: str, collection_name: str):
        self.document_store_mongo = DocumentStoreMongo(connection_string, database_name, collection_name)

    def exists_bytes(self, bytes_id: str) -> bool:
        return self.document_store_mongo.exists_document(bytes_id)

    def count_bytes(self) -> int:
        return self.document_store_mongo.count_document()

    def load_bytes(self, bytes_id: str) -> bytes:
        document = self.document_store_mongo.load_document(bytes_id)
        return b64decode(document["bytesbase64"])

    def load_bytes_all(self) -> Dict[str, bytes]:
        dict_document = self.document_store_mongo.load_document_all()
        dict_bytes = {}
        for bytes_id, document in dict_document.items():
            dict_bytes[bytes_id] = b64decode(document["bytesbase64"])
        return dict_bytes

    def delete_bytes(self, bytes_id: str) -> None:
        self.document_store_mongo.delete_document(bytes_id)

    def save_bytes(self, bytes_id: str, bytes: bytes) -> None:
        document = {"bytesbase64": b64encode(bytes).decode()}
        self.document_store_mongo.save_document(bytes_id, document)
