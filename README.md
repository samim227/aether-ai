# Aether

Aether is a small Python project that is the starting point for a future AI
assistant. This first version gives it two useful foundations: persistent
memory and a task list. Both are stored in a local SQLite database, so your
data is still there after you close and reopen the project.

This prototype does not connect to an AI model and does not run or write code
for you. In particular, it never executes generated code. Any future
self-improvement feature must use an isolated workspace, run automated tests,
keep backups, and have a way to roll back changes.

## Run Aether in GitHub Codespaces

1. Open this repository in GitHub Codespaces.
2. In VS Code, open the top menu and choose **Terminal > New Terminal**.
3. Install Aether and its test tool by running:

	```sh
	python -m pip install -e ".[test]"
	```

4. Try saving a memory and adding a task:

	```sh
	python -m aether memory set favorite_color blue
	python -m aether memory get favorite_color
	python -m aether task add "Explore how Aether should plan tasks"
	python -m aether task list
	```

5. Run the automated tests:

	```sh
	python -m pytest
	```

By default, Aether saves its database at `~/.aether/aether.sqlite3`. To keep
the database in another location, add `--db PATH` immediately after `python
-m aether`, for example `python -m aether --db ./aether.sqlite3 task list`.

## Commands

```text
python -m aether memory set KEY VALUE
python -m aether memory get KEY
python -m aether memory list
python -m aether memory delete KEY

python -m aether task add DESCRIPTION
python -m aether task list
python -m aether task status ID STATUS
```

Task statuses are `pending`, `in_progress`, `completed`, and `cancelled`.
The ID is shown when a task is created or listed.

## Project layout

- `aether/database.py` creates and opens the SQLite database.
- `aether/memory.py` stores and retrieves named pieces of memory.
- `aether/tasks.py` creates tasks and updates their status.
- `aether/cli.py` provides the commands you can run in the terminal.
- `tests/` checks that memory and tasks behave correctly and persist.

The modules are kept separate so a model integration or planning component
can be added later without putting AI behavior into the storage layer.