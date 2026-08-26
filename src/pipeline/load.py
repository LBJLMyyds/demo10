"""SQLite loading utilities."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.pipeline.config import DATABASE_PATH, SCHEMA_PATH


def prepare_for_sql(df: pd.DataFrame) -> pd.DataFrame:
    """Convert pandas missing values into SQLite-friendly nulls."""
    return df.astype(object).where(pd.notnull(df), None)


def recreate_database(database_path: Path = DATABASE_PATH, schema_path: Path = SCHEMA_PATH) -> sqlite3.Connection:
    """Create a fresh SQLite database from schema.sql."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        database_path.unlink()
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.executescript(schema_path.read_text())
    return connection


def load_tables(tables: dict[str, pd.DataFrame], connection: sqlite3.Connection) -> None:
    """Append cleaned tables into the SQLite database."""
    for table_name, df in tables.items():
        prepare_for_sql(df).to_sql(table_name, connection, if_exists="append", index=False)
    connection.commit()

