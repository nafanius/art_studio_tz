import csv
import pytest
from pathlib import Path
from art_studio_tz.api import DB

@pytest.fixture
def db(tmp_path):
    """Создаём экземпляр DB с временным CSV."""
    return DB(tmp_path, "quotes", ["text", "author"])

def test_create_and_read(db):
    item = {"text": "Hello", "author": "Someone"}
    new_id = db.create(item)
    assert new_id == 1

    row = db.read(new_id)
    assert row["id"] == "1"
    assert row["text"] == "Hello"
    assert row["author"] == "Someone"

def test_read_all(db):
    db.create({"text": "A", "author": "X"})
    db.create({"text": "B", "author": "Y"})
    all_rows = db.read_all()
    assert len(all_rows) == 2
    assert all_rows[0]["text"] == "A"
    assert all_rows[1]["author"] == "Y"

def test_update(db):
    id1 = db.create({"text": "Old", "author": "X"})
    db.update(id1, {"text": "New"})
    row = db.read(id1)
    assert row["text"] == "New"
    assert row["author"] == "X"

def test_delete(db):
    id1 = db.create({"text": "A", "author": "X"})
    id2 = db.create({"text": "B", "author": "Y"})
    db.delete(id1)
    all_rows = db.read_all()
    assert len(all_rows) == 1
    assert all_rows[0]["id"] == str(id2)

def test_delete_all(db):
    db.create({"text": "A", "author": "X"})
    db.create({"text": "B", "author": "Y"})
    db.delete_all()
    assert db.count() == 0
    assert db.read_all() == []

@pytest.mark.parametrize("num_records", [0, 1, 5])
def test_count(db, num_records):
    # добавляем num_records записей
    for i in range(num_records):
        db.create({"text": f"Q{i}", "author": f"A{i}"})
    assert db.count() == num_records

def test_update_non_existing(db):
    db.create({"text": "A", "author": "X"})
    db.update(999, {"text": "New"})
    # существующие записи остаются без изменени
    row = db.read(1)
    assert row["text"] == "A"

def test_delete_non_existing(db):
    db.create({"text": "A", "author": "X"})
    db.delete(999)  
    assert db.count() == 1