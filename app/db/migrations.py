import logging
from typing import Iterable

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def _table_exists(engine: Engine, table: str) -> bool:
    inspector = inspect(engine)
    try:
        return table in inspector.get_table_names()
    except Exception:  # noqa: BLE001
        return False


def _column_exists(engine: Engine, table: str, column: str) -> bool:
    inspector = inspect(engine)
    try:
        columns = inspector.get_columns(table)
    except Exception:  # noqa: BLE001
        return False
    return any(col.get("name") == column for col in columns)


def _add_column(engine: Engine, table: str, ddl: str) -> None:
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))


def _ensure_defaults(engine: Engine, table: str, assignments: Iterable[tuple[str, str]]) -> None:
    with engine.begin() as conn:
        for column, default in assignments:
            conn.execute(text(f"UPDATE {table} SET {column} = :default WHERE {column} IS NULL"), {"default": default})


def run_migrations(engine: Engine) -> None:
    if engine.dialect.name != "sqlite":
        logger.info("Automatic migrations are only handled for SQLite. Current dialect: %s", engine.dialect.name)
        return

    clothing_table = "clothing_items"
    migrations: list[tuple[str, str, str]] = [
        (clothing_table, "subtype", "subtype VARCHAR NOT NULL DEFAULT 'General'"),
        (clothing_table, "color_family", "color_family VARCHAR NOT NULL DEFAULT 'Other'"),
        (clothing_table, "season", "season VARCHAR NOT NULL DEFAULT 'All-season'"),
        (clothing_table, "name", "name VARCHAR(80) NOT NULL DEFAULT 'Untitled'"),
        (clothing_table, "updated_at", "updated_at DATETIME"),
    ]

    if _table_exists(engine, clothing_table):
        for table, column, ddl in migrations:
            if not _column_exists(engine, table, column):
                logger.info("Adding missing column %s.%s", table, column)
                _add_column(engine, table, ddl)

        _ensure_defaults(
            engine,
            clothing_table,
            [
                ("subtype", "General"),
                ("color_family", "Other"),
                ("season", "All-season"),
                ("name", "Untitled"),
            ],
        )
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    UPDATE clothing_items
                    SET updated_at = CURRENT_TIMESTAMP
                    WHERE updated_at IS NULL OR updated_at = 'CURRENT_TIMESTAMP'
                    """
                )
            )
