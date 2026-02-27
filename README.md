# SAFE-SQL: Privacy and Eco-Friendly DBMS Prototype

## Overview

SAFE-SQL acts as a middleware between users and the database to solve two critical problems:
1.  **Privacy**: Applies Differential Privacy (Laplace Noise) to query results to protect individual identities.
2.  **Sustainability**: Uses an "Eco-Scheduler" to batch queries, allowing the database to execute them in a single transaction, reducing energy consumption.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install psycopg2-binary codecarbon diffprivlib numpy
    ```

2.  **Database Configuration**:
    -   The system defaults to a **Mock Database** for demonstration if PostgreSQL is not available.
    -   To use a real PostgreSQL database, ensure `psycopg2` is installed and update the `db_config` dictionary in `backend/main.py` with your credentials.

## Running the Application

To start the interactive SAFE-SQL shell:

```bash
PYTHONPATH=. python3 backend/main.py
```

## Usage

1.  **Enter SQL Queries**: Type any SQL query (e.g., `SELECT avg(weight) FROM health_records`).
2.  **Observe Buffering**:
    -   The system will **hold** your query in a buffer.
    -   It waits until either **5 queries** are queued (Burst) OR **30 seconds** have passed (Timeout).
3.  **View Results**:
    -   Once the batch triggers, you will see an `[Energy]` log showing the kWh consumed for that batch.
    -   The query result will appear, with numerical values slightly altered by the Differential Privacy engine.

## Running Tests

To verify the "Burst" and "Timeout" logic:

```bash
PYTHONPATH=. python3 tests/verify_safesql.py
```
