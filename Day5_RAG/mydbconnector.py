"""Connect to local MySQL using settings from the .env beside this file."""

import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv


def get_connection():
    """Return an open connection; the caller is responsible for closing it."""
    load_dotenv(Path(__file__).with_name(".env"))
    settings = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "connection_timeout": 10,
    }
    database = os.getenv("MYSQL_DATABASE")
    if database:
        settings["database"] = database
    return mysql.connector.connect(**settings)


def execute_query(query: str) -> list[dict] | int:
    """Execute one SQL statement using a new connection.

    Return rows as dictionaries for result-producing statements, or the
    affected row count for writes. Commit successful statements, roll back
    on failure, and propagate errors to the caller.
    """
    connection = get_connection()
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall() if cursor.with_rows else cursor.rowcount
        connection.commit()
        return results
    except Exception:
        connection.rollback()
        raise
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            connection.close()


def get_schema(table_names: list[str]) -> dict[str, list[dict]]:
    """Return column definitions for one or more tables in MYSQL_DATABASE.

    Input:
        table_names: List of table names, e.g. ["actor", "film_actor"]

    Output:
        Dictionary mapping each table name to its column definitions.
    """

    if not isinstance(table_names, list) or not table_names:
        raise ValueError("table_names must be a non-empty list")

    schemas = {}

    for table_name in table_names:

        if not isinstance(table_name, str) or not table_name.strip():
            raise ValueError(
                "Each table name must be a non-empty string"
            )

        # Identifiers cannot use SQL value placeholders;
        # escape backticks instead.
        quoted_name = table_name.replace("`", "``")

        schemas[table_name] = execute_query(
            f"DESCRIBE `{quoted_name}`"
        )

    return schemas


def main():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        print(f"Connected to MySQL! Server version: {cursor.fetchone()[0]}")
        #print(get_schema("actor"))
    except (mysql.connector.Error, ValueError) as error:
        print(f"MySQL connection failed: {error}")
        return 1
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

