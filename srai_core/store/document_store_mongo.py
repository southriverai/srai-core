from typing import Dict, List, Optional

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from srai_core.store.document_store_base import DocumentStoreBase


class DocumentStoreMongo(DocumentStoreBase):
    def __init__(self, connection_string: str, database_name: str, collection_name: str):
        self.client = MongoClient(connection_string, server_api=ServerApi("1"))
        self.db = self.client.get_database(database_name)
        self.collection = self.db.get_collection(collection_name)

    def exists_document(self, document_id) -> bool:
        return self.collection.count_documents({"_id": document_id}) > 0

    def count_document(self) -> int:
        return self.collection.count_documents({})

    def load_document(self, document_id: str) -> None:
        document_result = self.collection.find_one({"_id": document_id})
        if document_result is None:
            return None
        return document_result["document"]

    def load_document_all(self) -> Dict[str, dict]:
        cursor_document_result = self.collection.find({})
        dict_document = {}
        for document_result in cursor_document_result:
            dict_document[document_result["_id"]] = document_result["document"]
        return dict_document

    # TODO: Implement load_document_for_query
    # def load_document_for_query(self, query: Dict[str, str]) -> Dict[str, dict]:
    #     # TODO limit query language
    #     cursor_document_result = self.collection.find(query)
    #     dict_document = {}
    #     for document_result in cursor_document_result:
    #         print(document_result)
    #         dict_document[document_result["_id"]] = document_result["document"]
    #     return dict_document

    def save_document(self, document_id: str, document: dict) -> None:
        self.collection.insert_one({"_id": document_id, "document": document})

    def delete_document(self, document_id: str) -> None:
        query = {"_id": document_id}
        self.collection.delete_one(query)

    def delete_document_all(self) -> int:
        delete_result = self.collection.delete_many({})
        return delete_result.deleted_count
