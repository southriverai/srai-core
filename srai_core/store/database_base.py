from abc import ABC, abstractmethod

from srai_core.store.bytes_store_base import BytesStoreBase
from srai_core.store.document_store_base import DocumentStoreBase


class DatabaseBase(ABC):
    def __init__(self, database_name: str):
        self.database_name = database_name

    @abstractmethod
    def get_document_store(self, collection_name: str) -> DocumentStoreBase:
        raise NotImplementedError()

    @abstractmethod
    def get_bytes_store(self, collection_name: str) -> BytesStoreBase:
        raise NotImplementedError()
