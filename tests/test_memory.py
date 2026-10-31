import pytest

from aether.database import Database
from aether.memory import MemoryStore


def test_memory_can_be_saved_updated_and_loaded_again(tmp_path):
    database_path = tmp_path / "aether.sqlite3"
    first_store = MemoryStore(Database(database_path))

    first_store.save("favorite_color", "blue")
    first_store.save("favorite_color", "green")

    reopened_store = MemoryStore(Database(database_path))
    entry = reopened_store.get("favorite_color")
    assert entry is not None
    assert entry.value == "green"
    assert [item.key for item in reopened_store.list()] == ["favorite_color"]


def test_memory_delete_reports_whether_an_entry_existed(tmp_path):
    store = MemoryStore(Database(tmp_path / "aether.sqlite3"))
    store.save("note", "Remember this")

    assert store.delete("note") is True
    assert store.delete("note") is False
    assert store.get("note") is None


def test_memory_rejects_an_empty_key(tmp_path):
    store = MemoryStore(Database(tmp_path / "aether.sqlite3"))

    with pytest.raises(ValueError, match="Memory key cannot be empty"):
        store.save("  ", "value")