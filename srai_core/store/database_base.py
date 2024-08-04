from abc import ABC, abstractmethod
from typing import Type, TypeVar

from pydantic import BaseModel

from srai_core.store.bytes_store_base import BytesStoreBase
from srai_core.store.dir_store_base import DirStoreBase
from srai_core.store.dir_store_bytes_store import DirStoreBytesStore
from srai_core.store.document_store_base import DocumentStoreBase
from srai_core.store.object_store import ObjectStore

T = TypeVar("T", bound=BaseModel)


class DatabaseBase(ABC):
    def __init__(self, database_name: str):
        self.database_name = database_name

    def get_object_store(self, collection_name: str, model_class: Type[T]) -> ObjectStore[T]:
        return ObjectStore[model_class](self.get_document_store(collection_name), model_class)

    @abstractmethod
    def get_document_store(self, collection_name: str) -> DocumentStoreBase:
        raise NotImplementedError()

    @abstractmethod
    def get_bytes_store(self, collection_name: str) -> BytesStoreBase:
        raise NotImplementedError()

    def get_dir_store(self, collection_name: str) -> DirStoreBase:
        return DirStoreBytesStore(self.get_bytes_store(collection_name))
