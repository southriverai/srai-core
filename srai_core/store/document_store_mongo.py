from typing import Dict, List, Optional, Tuple

from pymongo.mongo_client import MongoClient

from srai_core.store.document_store_base import DocumentStoreBase


class DocumentStoreMongo(DocumentStoreBase):

    def __init__(self, client: MongoClient, database_name: str, collection_name: str):
        self.client = client
        self.db = self.client.get_database(database_name)
        self.collection = self.db.get_collection(collection_name)

    def exists_document(self, document_id) -> bool:
        return self.collection.count_documents({"_id": document_id}) > 0

    def count_document(self) -> int:
        return self.collection.count_documents({})

    def load_document(self, document_id: str) -> dict:
        return self.try_load_document(document_id, raise_if_missing=True)  # type: ignore

    def load_list_document_id(self) -> list:
        cursor_document_result = self.collection.find({})
        return [document_result["_id"] for document_result in cursor_document_result]

    def try_load_document(self, document_id: str, raise_if_missing=False) -> Optional[dict]:
        document_result = self.collection.find_one({"_id": document_id})
        if raise_if_missing and document_result is None:
            raise Exception(f"Document with id '{document_id}' not found")
        if document_result is None:
            return None
        return document_result["document"]

    def load_document_all(self) -> Dict[str, dict]:
        cursor_document_result = self.collection.find({})
        dict_document = {}
        for document_result in cursor_document_result:
            dict_document[document_result["_id"]] = document_result["document"]
        return dict_document

    def load_document_dict_for_query(
        self,
        query: Dict[str, str],
        order_by: List[Tuple[str, bool]] = [],
        limit: int = 0,
        offset: int = 0,
    ) -> Dict[str, dict]:
        query_mod = {}
        for key in query:
            query_mod["document." + key] = query[key]
        order_mod = []
        for field, asc in order_by:
            order_mod.append(("document." + field, 1 if asc else -1))

        cursor = self.collection.find(query_mod)
        # check if cursor is empty
        # if not cursor.alive:
        #     return {}
        if len(order_mod) > 0:
            cursor = cursor.sort(order_mod)
        if limit > 0:
            cursor = cursor.limit(limit)
        if offset > 0:
            cursor = cursor.skip(offset)

        dict_document = {}
        for document_result in cursor:
            dict_document[document_result["_id"]] = document_result["document"]
        return dict_document

    def save_document(self, document_id: str, document: dict, update_if_exist=True) -> None:
        if update_if_exist and self.exists_document(document_id):
            self.collection.update_one({"_id": document_id}, {"$set": {"document": document}})
        else:
            self.collection.insert_one({"_id": document_id, "document": document})

    def delete_document(self, document_id: str) -> None:
        query = {"_id": document_id}
        self.collection.delete_one(query)

    def delete_document_all(self) -> int:
        delete_result = self.collection.delete_many({})
        return delete_result.deleted_count
