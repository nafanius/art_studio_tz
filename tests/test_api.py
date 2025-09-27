from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch
import art_studio_tz
import pytest
from datetime import datetime, timezone
from art_studio_tz import Quote, QuoteDB, MissingText, InvalidQuoteId, QuoteDBsql

@pytest.fixture()
def quote_db():
        with TemporaryDirectory() as db_dir:
            db_path = Path(db_dir)
            db = art_studio_tz.QuoteDB(db_path)
            yield db


class TestQuote:
    def test_quote_creation(self):
        q = Quote(text="Hello world", author="Max", timestep="2025-09-27")
        assert q.text == "Hello world"
        assert q.author == "Max"
        assert q.timestep == "2025-09-27"
        assert q.id is None

    def test_quote_default_values(self):
        q = Quote()
        assert q.text is None
        assert q.author is None
        assert q.timestep is None
        assert q.id is None

    def test_quote_comparison_ignores_id(self):
        q1 = Quote(text="Hello", author="Alice", timestep="t1", id=1)
        q2 = Quote(text="Hello", author="Alice", timestep="t1", id=2)
        assert q1 == q2  # сравнение игнорирует id

    def test_quote_different_objects(self):
        q1 = Quote(text="Hello", author="Alice")
        q2 = Quote(text="Hello", author="Bob")
        assert q1 != q2

    def test_to_dict(self):
        q = Quote(text="Hello", author="Alice", timestep="t1", id=10)
        d = q.to_dict()
        expected = {"text": "Hello", "author": "Alice", "timestep": "t1", "id": 10}
        assert d == expected

    def test_from_dict(self):
        data = {"text": "Hello", "author": "Alice", "timestep": "t1", "id": 10}
        q = Quote.from_dict(data)
        assert isinstance(q, Quote)
        assert q.text == "Hello"
        assert q.author == "Alice"
        assert q.timestep == "t1"
        assert q.id == 10


class TestQuoteDB:
    @pytest.fixture(autouse=True)
    def setup(self):
        with patch("art_studio_tz.api.DB") as MockDB:
            self.mock_db = MagicMock()
            MockDB.return_value = self.mock_db
            self.quote_db = QuoteDB(Path("fake_path"))
            yield

    @pytest.mark.parametrize("text,author", [
        ("Hello", "Someone"),
        ("Another quote", "Author"),
        ("Quote without author", None),
    ])
    def test_add_quote_returns_id(self, text, author):
        quote = Quote(text=text, author=author)
        self.mock_db.create.return_value = 1

        quote_id = self.quote_db.add_quote(quote)

        self.mock_db.create.assert_called_once_with(quote.to_dict())
        assert quote_id == 1
        args, kwargs = self.mock_db.update.call_args
        assert args[0] == 1
        assert "timestep" in args[1]

    def test_add_quote_missing_text_raises(self):
        quote = Quote(text=None, author="Someone")
        with pytest.raises(MissingText):
            self.quote_db.add_quote(quote)

    @pytest.mark.parametrize("data", [
        {"text": "Hello", "author": "Someone", "id": 1},
        {"text": "Test", "author": "Alice", "id": 2},
    ])
    def test_get_quote_returns_quote(self, data):
        self.mock_db.read.return_value = data
        quote = self.quote_db.get_quote(data["id"])
        assert isinstance(quote, Quote)
        assert quote.text == data["text"]
        assert quote.author == data["author"]

    def test_get_quote_invalid_id_raises(self):
        self.mock_db.read.return_value = None
        with pytest.raises(InvalidQuoteId):
            self.quote_db.get_quote(999)

    @pytest.mark.parametrize("all_quotes,author_filter,expected_count", [
        (
            [{"text": "A", "author": "X", "id": 1},
             {"text": "B", "author": "Y", "id": 2}],
            "X", 1
        ),
        (
            [{"text": "A", "author": "X", "id": 1},
             {"text": "B", "author": "Y", "id": 2}],
            "Y", 1
        ),
        (
            [{"text": "A", "author": "X", "id": 1},
             {"text": "B", "author": "Y", "id": 2}],
            None, 2
        ),
    ])
    def test_list_quote_filters_by_author(self, all_quotes, author_filter, expected_count):
        self.mock_db.read_all.return_value = all_quotes
        quotes = self.quote_db.list_quote(author=author_filter)
        assert len(quotes) == expected_count

    @pytest.mark.parametrize("count_val", [0, 1, 5, 42])
    def test_count_calls_db_count(self, count_val):
        self.mock_db.count.return_value = count_val
        assert self.quote_db.count() == count_val

    def test_update_quote_calls_db_update(self):
        quote_mod = Quote(text="New text", author="New author")
        self.quote_db.update_qote(1, quote_mod)
        self.mock_db.update.assert_called_once_with(1, quote_mod.to_dict())

    def test_update_quote_invalid_id_raises(self):
        quote_mod = Quote(text="New text", author="New author")
        self.mock_db.update.side_effect = KeyError
        with pytest.raises(InvalidQuoteId):
            self.quote_db.update_qote(999, quote_mod)

    def test_delete_quote_calls_db_delete(self):
        self.quote_db.delete_quote(1)
        self.mock_db.delete.assert_called_once_with(1)

    def test_delete_quote_invalid_id_raises(self):
        self.mock_db.delete.side_effect = KeyError
        with pytest.raises(InvalidQuoteId):
            self.quote_db.delete_quote(999)

    def test_delete_all_calls_db_delete_all(self):
        self.quote_db.delete_all()
        self.mock_db.delete_all.assert_called_once()

class TestQuoteDBsql:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Патчим DBsql там, где QuoteDBsql его реально использует
        with patch("art_studio_tz.api.DBsql") as MockDBsql:
            self.mock_db = MagicMock()
            MockDBsql.return_value = self.mock_db
            self.db_sql = QuoteDBsql("user", "pass")
            yield

    @pytest.mark.parametrize("text,author", [
        ("Hello", "Someone"),
        ("Another quote", "Author"),
        ("Quote without author", None),
    ])
    def test_add_quote_sql(self, text, author):
        quote = Quote(text=text, author=author)
        self.db_sql.add_quote_sql(quote)
        self.mock_db.create.assert_called_once_with(quote.to_dict())

    def test_add_quote_sql_missing_text_raises(self):
        quote = Quote(text=None, author="Someone")
        with pytest.raises(MissingText):
            self.db_sql.add_quote_sql(quote)

    @pytest.mark.parametrize("all_quotes,author_filter,expected_count", [
        (
            [{"text": "A", "author": "X", "id": 1},
             {"text": "B", "author": "Y", "id": 2}],
            "X", 1
        ),
        (
            [{"text": "A", "author": "X", "id": 1},
             {"text": "B", "author": "Y", "id": 2}],
            "Y", 1
        ),
        (
            [{"text": "A", "author": "X", "id": 1},
             {"text": "B", "author": "Y", "id": 2}],
            None, 2
        ),
    ])
    def test_list_quote(self, all_quotes, author_filter, expected_count):
        self.mock_db.read_all.return_value = all_quotes
        quotes = self.db_sql.list_quote(author=author_filter)
        assert len(quotes) == expected_count
        for q, data in zip(quotes, [t for t in all_quotes if author_filter is None or t["author"] == author_filter]):
            assert q.text == data["text"]
            assert q.author == data["author"]

    @patch("art_studio_tz.api.requests.get")
    @patch("time.sleep", return_value=None)  # чтобы не ждать паузы
    def test_get_some_quotes(self, mock_sleep, mock_get):
        mock_get.return_value.json.return_value = [
            {"q": "Quote1", "a": "Author1"},
            {"q": "Quote2", "a": "Author2"},
        ]
        mock_get.return_value.raise_for_status = lambda: None

        self.db_sql.add_quote_sql = MagicMock()  # Мокаем метод, чтобы проверить вызовы

        self.db_sql.get_some_quotes("fake_url")

        assert self.db_sql.add_quote_sql.call_count == 2
        self.db_sql.add_quote_sql.assert_any_call(Quote(text="Quote1", author="Author1"))
        self.db_sql.add_quote_sql.assert_any_call(Quote(text="Quote2", author="Author2"))

    @pytest.mark.parametrize("number,return_data", [
        (1, [{"text": "A", "author": "X"}]),
        (3, [{"text": "A", "author": "X"}, {"text": "B", "author": "Y"}, {"text": "C", "author": "Z"}]),
    ])
    def test_get_latest(self, number, return_data):
        self.mock_db.get_latest.return_value = return_data
        quotes = self.db_sql.get_latest(number)
        assert len(quotes) == len(return_data)
        for q, data in zip(quotes, return_data):
            assert q.text == data["text"]
            assert q.author == data["author"]

    def test_delete_all(self):
        self.db_sql.delete_all()
        self.mock_db.delete_all.assert_called_once()

def test_empty(quote_db):
    assert quote_db.count() == 0 

