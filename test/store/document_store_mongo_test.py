import os

from srai_core.store.document_store_mongo import DocumentStoreMongo
from srai_core.tools_env import get_string_from_env


# TODO convert to pytest
def test_all() -> None:
    connection_string = get_string_from_env("MONGODB_CONNECTION_STRING")
    database_name = "test_database"
    collection_name = "test_collection"
    store = DocumentStoreMongo(connection_string, database_name, collection_name)
    print("clear store")
    store.delete_document_all()
    assert store.count_document() == 0
    store.save_document("1", {"name": "test"})
    assert store.count_document() == 1
    assert store.exists_document("1")
    assert not store.exists_document("2")
    assert store.load_document("1") == {"name": "test"}
    assert store.load_document_all() == {"1": {"name": "test"}}
    assert store.load_document_for_query({"name": "test"}) == {"1": {"name": "test"}}
    # delete store
    store.delete_document_all()
    store.client.drop_database(database_name)


if __name__ == "__main__":
    test_all()
