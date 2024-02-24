import os

from srai_core.store.document_store_disk import DocumentStoreDisk


# TODO convert to pytest
def test_all() -> None:
    path_dir = "test_store"
    store = DocumentStoreDisk(path_dir)
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
    list_file = os.listdir(path_dir)
    if 0 < len(list_file):
        print("failed to delete store")
    for file in list_file:
        os.remove(os.path.join(path_dir, file))
    os.rmdir(path_dir)


if __name__ == "__main__":
    test_all()
