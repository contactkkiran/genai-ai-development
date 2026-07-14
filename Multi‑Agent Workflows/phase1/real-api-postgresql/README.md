# Real API PostgreSQL Project

This folder contains prototype code for agentic API workflows with PostgreSQL and event loop handling.

## Contents

- `eventloop_single_agent_multi_task.py` — Multi-task event loop example.
- `eventloop_single_agent_single_task.py.py` — Single-task event loop example.

## Purpose

- Learn how to structure simple agent tasks within an event loop.
- Explore basic PostgreSQL-backed API patterns.

## Running the examples

1. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install any required packages as needed:

```bash
pip install psycopg2-binary
```

3. Run the selected script:

```bash
python eventloop_single_agent_single_task.py.py
```

## Notes

- Update the script filenames or import paths if needed.
- These files are prototypes for learning agent event loop behavior.
