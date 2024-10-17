from pymongo import MongoClient

from srai_core.store.document_store_mongo import DocumentStoreMongo
from srai_core.tools_env import get_string_from_env


# TODO convert to pytest
def test_all() -> None:
    connection_string = get_string_from_env("MONGODB_CONNECTION_STRING")
    database_name = "test_database"
    collection_name = "test_collection"
    client = MongoClient(connection_string)
    store = DocumentStoreMongo(client, database_name, collection_name)
    document_1 = {"name": "test", "time": 1}
    document_2 = {"name": "test", "time": 2}
    print("clear store")
    store.delete_document_all()
    assert store.count_document() == 0
    store.save_document("1", document_1)
    assert store.count_document() == 1
    assert store.exists_document("1")
    assert not store.exists_document("2")
    assert store.load_document("1") == document_1
    assert store.load_document_all() == {"1": document_1}
    assert store.load_document_for_query({"name": "test"}) == document_1
    assert store.load_document_dict_for_query({"name": "test"}) == {"1": document_1}
    store.save_document("2", document_2)
    assert store.load_document_dict_for_query({"name": "test"}, limit=1) == {"1": document_1}
    assert store.load_document_dict_for_query({"name": "test"}, limit=1, order_by=[("time", True)]) == {"1": document_1}
    assert store.load_document_dict_for_query({"name": "test"}, limit=1, order_by=[("time", False)]) == {
        "2": document_2
    }

    # delete store
    store.delete_document_all()
    store.client.drop_database(database_name)


if __name__ == "__main__":
    test_all()
