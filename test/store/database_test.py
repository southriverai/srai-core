import os
import shutil

from srai_core.store.database_base import DatabaseBase
from srai_core.store.database_disk import DatabaseDisk
from srai_core.store.database_memory import DatabaseMemory
from srai_core.store.database_mongo import DatabaseMongo
from srai_core.tools_env import get_string_from_env

# TODO convert to pytest


def get_memory() -> DatabaseBase:
    print("test database memory")
    database_name = "test_database"
    return DatabaseMemory(database_name)


def get_disk() -> DatabaseBase:
    print("test database disk")
    database_name = "test_database"
    path_dir_database = "test_database"
    return DatabaseDisk(database_name, path_dir_database)


def get_mongo() -> DatabaseBase:
    connection_string = get_string_from_env("MONGODB_CONNECTION_STRING")
    database_name = "test_database"
    return DatabaseMongo(database_name, connection_string)


def test_database(database: DatabaseBase) -> None:
    collection_name = "test_collection"
    document_store = database.get_document_store(collection_name)
    print("clear store")
    document_store.delete_document_all()
    assert document_store.count_document() == 0
    document_store.save_document("1", {"name": "test"})
    assert document_store.count_document() == 1
    assert document_store.exists_document("1")
    assert not document_store.exists_document("2")
    assert document_store.load_document("1") == {"name": "test"}
    assert document_store.load_document_all() == {"1": {"name": "test"}}
    assert document_store.load_document_for_query({"name": "test"}) == {"1": {"name": "test"}}
    document_store.save_document("1", {"name": "test"})
    # delete store
    document_store.delete_document_all()
    # database.delete(database_name)

    collection_name = "test_collection_dir"
    dir_store = database.get_dir_store(collection_name)
    print("clear store")
    dir_store.delete_dir_all()
    assert dir_store.count_dir() == 0
    path_dir_source = os.path.join("test", "data", "dir_source")
    path_dir_target = os.path.join("test", "data", "dir_target")
    dir_store.save_dir("1", path_dir_source)
    assert dir_store.count_dir() == 1
    assert dir_store.exists_dir("1")
    assert not dir_store.exists_dir("2")
    dir_store.load_dir("1", path_dir_target)
    assert os.path.isfile(os.path.join(path_dir_target, "test.txt"))
    assert os.path.isfile(os.path.join(path_dir_target, "inner", "test2.txt"))
    # TODO delete path dir target

    # delete store
    dir_store.delete_dir_all()

    # delete dir
    shutil.rmtree(path_dir_target)


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
    print("test database")

    # test_database(get_memory())
    # test_database(get_disk())
    test_database(get_mongo())
    # test_migrate(get_disk(), get_mongo())
