"""Persistent task management backed by SQLite."""

import sqlite3
from dataclasses import dataclass
from enum import Enum

from aether.database import Database, utc_now


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class Task:
    id: int
    description: str
    status: TaskStatus
    created_at: str
    updated_at: str


class TaskManager:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, description: str) -> Task:
        description = description.strip()
        if not description:
            raise ValueError("Task description cannot be empty.")

        created_at = utc_now()
        with self.database.connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (description, status, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (description, TaskStatus.PENDING.value, created_at, created_at),
            )
            task_id = cursor.lastrowid
        if task_id is None:
            raise RuntimeError("The database did not return the new task ID.")
        task = self.get(task_id)
        if task is None:
            raise RuntimeError("The new task could not be loaded from the database.")
        return task

    def get(self, task_id: int) -> Task | None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT id, description, status, created_at, updated_at FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
        if row is None:
            return None
        return self._from_row(row)

    def list(self, status: TaskStatus | str | None = None) -> list[Task]:
        with self.database.connection() as connection:
            if status is None:
                rows = connection.execute(
                    "SELECT id, description, status, created_at, updated_at FROM tasks ORDER BY id"
                ).fetchall()
            else:
                task_status = TaskStatus(status)
                rows = connection.execute(
                    """
                    SELECT id, description, status, created_at, updated_at
                    FROM tasks WHERE status = ? ORDER BY id
                    """,
                    (task_status.value,),
                ).fetchall()
        return [self._from_row(row) for row in rows]

    def update_status(self, task_id: int, status: TaskStatus | str) -> Task | None:
        task_status = TaskStatus(status)
        with self.database.connection() as connection:
            cursor = connection.execute(
                "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
                (task_status.value, utc_now(), task_id),
            )
            if cursor.rowcount == 0:
                return None
        return self.get(task_id)

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            description=row["description"],
            status=TaskStatus(row["status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )