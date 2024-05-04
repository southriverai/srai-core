import os
from re import A

from srai_core.store import database_mongo
from srai_core.store.database_base import DatabaseBase
from srai_core.store.database_disk import DatabaseDisk
from srai_core.store.database_mongo import DatabaseMongo
from srai_core.store.document_store_mongo import DocumentStoreMongo
from srai_core.tools_env import get_string_from_env


# TODO convert to pytest
def get_mongo() -> DatabaseBase:
    connection_string = get_string_from_env("MONGODB_CONNECTION_STRING")
    database_name = "test_database"
    return DatabaseMongo(database_name, connection_string)


def get_disk() -> DatabaseBase:
    database_name = "test_database"
    path_dir_database = "test_database"
    return DatabaseDisk(database_name, path_dir_database)


def test_database(database: DatabaseBase) -> None:
    collection_name = "test_collection"
    store = database.get_document_store(collection_name)
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
    # database.delete(database_name)


def test_migrate(database_from: DatabaseBase, database_to: DatabaseBase):
    collection_name = "test_collection"
    store_from = database_from.get_document_store(collection_name)
    store_to = database_to.get_document_store(collection_name)
    print("clear store")
    store_from.delete_document_all()
    store_to.delete_document_all()
    assert store_from.count_document() == 0
    assert store_to.count_document() == 0

    store_from.save_document("1", {"name": "test"})
    assert store_from.count_document() == 1
    assert store_from.exists_document("1")
    assert not store_from.exists_document("2")
    assert store_from.load_document("1") == {"name": "test"}
    assert store_from.load_document_all() == {"1": {"name": "test"}}
    assert store_from.load_document_for_query({"name": "test"}) == {"1": {"name": "test"}}
    # delete store

    store_from.copy_to(store_to)
    assert store_to.count_document() == 1
    assert store_to.exists_document("1")
    assert not store_to.exists_document("2")
    assert store_to.load_document("1") == {"name": "test"}
    assert store_to.load_document_all() == {"1": {"name": "test"}}
    assert store_to.load_document_for_query({"name": "test"}) == {"1": {"name": "test"}}

    store_from.delete_document_all()
    store_to.delete_document_all()
    # database.delete(database_name)


if __name__ == "__main__":
    test_database(get_mongo())
    test_database(get_disk())
    test_migrate(get_disk(), get_mongo())
