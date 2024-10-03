from typing import Dict, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel

from srai_core.store.document_store_base import DocumentStoreBase

T = TypeVar("T", bound=BaseModel)


class ObjectStore(Generic[T]):

    def __init__(self, document_store: DocumentStoreBase, model_class: Type[T]):
        self.document_store = document_store
        self.model_class = model_class

    def _document_to_object(self, document: dict) -> T:
        return self.model_class(**document)  # type: ignore

    def copy_to(self, store_to: "DocumentStoreBase") -> None:
        self.document_store.copy_to(store_to)

    def exists_object(self, document_id: str) -> bool:
        return self.document_store.exists_document(document_id)

    def count_object(self) -> int:
        return self.document_store.count_document()

    def load_object(self, document_id: str) -> T:
        document = self.document_store.load_document(document_id)
        return self._document_to_object(document)

    def try_load_object(self, bytes_id: str) -> Optional[T]:
        if self.document_store.exists_document(bytes_id):
            return self.load_object(bytes_id)
        else:
            return None

    def load_object_all(self) -> Dict[str, T]:
        dict_document = self.document_store.load_document_all()
        dict_object = {}
        for document_id, document in dict_document.items():
            dict_object[document_id] = self._document_to_object(document)
        return dict_object

    def load_list_object_id(self) -> List[str]:
        return self.document_store.load_list_document_id()

    def load_object_dict_for_query(self, query: Dict[str, str], limit: int = 0, offset: int = 0) -> Dict[str, T]:
        dict_document = self.document_store.load_document_dict_for_query(query, limit, offset)
        dict_object = {}
        for document_id, document in dict_document.items():
            dict_object[document_id] = self._document_to_object(document)
        return dict_object

    def load_object_for_query(self, query: Dict[str, str]) -> Optional[T]:
        document = self.document_store.load_document_for_query(query)
        if document is not None:
            return self._document_to_object(document)
        else:
            return None

    def delete_object(self, object_id: str) -> None:
        self.document_store.delete_document(object_id)

    def delete_object_all(self) -> int:
        list_object_id = self.load_list_object_id()
        for object_id in list_object_id:
            self.delete_object(object_id)
        return len(list_object_id)

    def save_object(self, object_id: str, object: T) -> None:
        document = object.model_dump()
        self.document_store.save_document(object_id, document)
