"""Persistent named memories backed by SQLite."""

from dataclasses import dataclass

from aether.database import Database, utc_now


@dataclass(frozen=True, slots=True)
class MemoryEntry:
    key: str
    value: str
    updated_at: str


class MemoryStore:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save(self, key: str, value: str) -> MemoryEntry:
        key = key.strip()
        if not key:
            raise ValueError("Memory key cannot be empty.")

        updated_at = utc_now()
        with self.database.connection() as connection:
            connection.execute(
                """
                INSERT INTO memories (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
                """,
                (key, value, updated_at),
            )
        return MemoryEntry(key=key, value=value, updated_at=updated_at)

    def get(self, key: str) -> MemoryEntry | None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT key, value, updated_at FROM memories WHERE key = ?",
                (key.strip(),),
            ).fetchone()
        if row is None:
            return None
        return MemoryEntry(key=row["key"], value=row["value"], updated_at=row["updated_at"])

    def list(self) -> list[MemoryEntry]:
        with self.database.connection() as connection:
            rows = connection.execute(
                "SELECT key, value, updated_at FROM memories ORDER BY key"
            ).fetchall()
        return [
            MemoryEntry(key=row["key"], value=row["value"], updated_at=row["updated_at"])
            for row in rows
        ]

    def delete(self, key: str) -> bool:
        with self.database.connection() as connection:
            cursor = connection.execute("DELETE FROM memories WHERE key = ?", (key.strip(),))
        return cursor.rowcount > 0