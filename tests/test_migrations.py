from sqlalchemy import create_engine, inspect, text

from app.db.migrations import run_migrations


def test_run_migrations_adds_metadata_columns(tmp_path):
    db_path = tmp_path / "legacy.db"
    engine = create_engine(f"sqlite:///{db_path}")

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE clothing_items (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    category VARCHAR NOT NULL,
                    color VARCHAR NOT NULL
                )
                """
            )
        )
        conn.execute(text("INSERT INTO clothing_items (user_id, category, color) VALUES (1, 'top', 'navy')"))

    run_migrations(engine)

    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("clothing_items")}
    assert {"subtype", "color_family", "season"}.issubset(columns)

    with engine.connect() as conn:
        row = conn.execute(text("SELECT subtype, color_family, season FROM clothing_items WHERE id = 1")).one()

    assert row.subtype == "General"
    assert row.color_family == "Other"
    assert row.season == "All-season"
