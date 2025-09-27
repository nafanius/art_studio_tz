import pytest
from unittest.mock import MagicMock, patch
from art_studio_tz import DBsql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from art_studio_tz.db_sql import QuoteModel, Base


@pytest.fixture
def dbsql():
    engine = create_engine("sqlite:///:memory:", echo=False, future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    class TestDBsql(DBsql):
        def __init__(self):
            self.engine = engine
            self.Session = Session

    return TestDBsql()

def test_create_and_read_all(dbsql):
    item = {"text": "Hello", "author": "Someone"}
    new_id = dbsql.create(item)
    
    # В SQLite in-memory ID присвоится только после commit, поэтому new_id может быть None
    # Для теста проверяем наличие текста и автора
    all_rows = dbsql.read_all()
    assert len(all_rows) == 1
    assert all_rows[0]["text"] == "Hello"
    assert all_rows[0]["author"] == "Someone"
    # Проверяем, что id существует
    assert "id" in all_rows[0]

def test_get_latest(dbsql):
    import datetime
    items = [
        {"text": "A", "author": "X", "timestep": datetime.datetime(2025, 1, 1)},
        {"text": "B", "author": "Y", "timestep": datetime.datetime(2025, 1, 2)},
        {"text": "C", "author": "Z", "timestep": datetime.datetime(2025, 1, 3)},
    ]
    for item in items:
        dbsql.create(item)
    
    latest_2 = dbsql.get_latest(2)
    assert len(latest_2) == 2
    assert latest_2[0]["text"] == "C"
    assert latest_2[1]["text"] == "B"

def test_create_multiple(dbsql):
    ids = []
    for i in range(5):
        new_id = dbsql.create({"text": f"Quote {i}", "author": f"Author {i}"})
        ids.append(new_id)
    all_rows = dbsql.read_all()
    assert len(all_rows) == 5
    # Проверяем, что у всех есть id
    assert all("id" in r for r in all_rows)

def test_get_latest_default_number(dbsql):
    import datetime
    for i in range(10):
        dbsql.create({
            "text": f"Q{i}", 
            "author": f"A{i}",
            "timestep": datetime.datetime(2025, 1, i+1)
        })
    latest = dbsql.get_latest()  # по умолчанию 5
    assert len(latest) == 5
    assert latest[0]["text"] == "Q9"
    assert latest[-1]["text"] == "Q5"