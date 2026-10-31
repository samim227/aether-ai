"""Command-line interface for Aether's memory and task features."""

import argparse
from pathlib import Path

from aether.database import Database
from aether.memory import MemoryStore
from aether.tasks import TaskManager, TaskStatus


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aether", description="Aether memory and task manager")
    parser.add_argument("--db", type=Path, help="SQLite database file (default: ~/.aether/aether.sqlite3)")
    areas = parser.add_subparsers(dest="area", required=True)

    memory = areas.add_parser("memory", help="Save and look up memories")
    memory_commands = memory.add_subparsers(dest="command", required=True)
    save_memory = memory_commands.add_parser("set", help="Save a memory")
    save_memory.add_argument("key")
    save_memory.add_argument("value")
    get_memory = memory_commands.add_parser("get", help="Look up a memory")
    get_memory.add_argument("key")
    memory_commands.add_parser("list", help="List saved memories")
    delete_memory = memory_commands.add_parser("delete", help="Delete a memory")
    delete_memory.add_argument("key")

    task = areas.add_parser("task", help="Create and update tasks")
    task_commands = task.add_subparsers(dest="command", required=True)
    add_task = task_commands.add_parser("add", help="Create a task")
    add_task.add_argument("description")
    task_commands.add_parser("list", help="List tasks")
    set_status = task_commands.add_parser("status", help="Change a task's status")
    set_status.add_argument("id", type=int)
    set_status.add_argument("status", choices=[status.value for status in TaskStatus])
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    database = Database(args.db)

    if args.area == "memory":
        memories = MemoryStore(database)
        if args.command == "set":
            memories.save(args.key, args.value)
            print(f"Saved memory: {args.key}")
        elif args.command == "get":
            entry = memories.get(args.key)
            if entry is None:
                print(f"No memory found for key: {args.key}")
                return 1
            print(entry.value)
        elif args.command == "list":
            entries = memories.list()
            if not entries:
                print("No memories saved.")
            for entry in entries:
                print(f"{entry.key}: {entry.value}")
        elif args.command == "delete":
            if memories.delete(args.key):
                print(f"Deleted memory: {args.key}")
            else:
                print(f"No memory found for key: {args.key}")
                return 1
        return 0

    tasks = TaskManager(database)
    if args.command == "add":
        task = tasks.create(args.description)
        print(f"Created task #{task.id}: {task.description} [{task.status.value}]")
    elif args.command == "list":
        items = tasks.list()
        if not items:
            print("No tasks saved.")
        for task in items:
            print(f"#{task.id} [{task.status.value}] {task.description}")
    elif args.command == "status":
        task = tasks.update_status(args.id, args.status)
        if task is None:
            print(f"No task found with ID {args.id}")
            return 1
        print(f"Updated task #{task.id}: {task.status.value}")
    return 0