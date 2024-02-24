from abc import ABC, abstractmethod
from typing import Dict


class DocumentStoreBase(ABC):
    # file store for

    def __init__(self) -> None:
        pass

    @abstractmethod
    def exists_document(self, document_id: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def count_document(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def load_document(self, document_id: str) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def load_document_all(self) -> Dict[str, dict]:
        raise NotImplementedError()

    def load_document_for_query(self, query: Dict[str, str]) -> Dict[str, dict]:
        dict_document = self.load_document_all()
        dict_selected = {}
        for document_id, document in dict_document.items():
            for key in query:
                if query not in document:
                    continue
                if document[key] == query[key]:
                    dict_selected[document_id] = document
        return dict_selected

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def save_document(self, document_id: str, document: dict) -> None:
        raise NotImplementedError()
