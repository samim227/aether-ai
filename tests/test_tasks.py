import pytest

from aether.database import Database
from aether.tasks import TaskManager, TaskStatus


def test_task_is_persisted_and_status_can_be_updated(tmp_path):
    database_path = tmp_path / "aether.sqlite3"
    first_manager = TaskManager(Database(database_path))
    created = first_manager.create("Build the first prototype")

    updated = first_manager.update_status(created.id, TaskStatus.IN_PROGRESS)

    assert updated is not None
    assert updated.status is TaskStatus.IN_PROGRESS
    reopened_manager = TaskManager(Database(database_path))
    assert reopened_manager.get(created.id) == updated
    assert reopened_manager.list(status="in_progress") == [updated]


def test_task_rejects_an_empty_description(tmp_path):
    manager = TaskManager(Database(tmp_path / "aether.sqlite3"))

    with pytest.raises(ValueError, match="Task description cannot be empty"):
        manager.create("  ")


def test_task_rejects_an_unknown_status(tmp_path):
    manager = TaskManager(Database(tmp_path / "aether.sqlite3"))
    task = manager.create("Write tests")

    with pytest.raises(ValueError):
        manager.update_status(task.id, "started")