import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from art_studio_tz.cli import app
from art_studio_tz import InvalidQuoteId
import art_studio_tz as packet

runner = CliRunner()

@pytest.fixture
def mock_quote_db():
    with patch("art_studio_tz.cli.quote_db") as mock:
        db_instance = MagicMock()
        mock.return_value.__enter__.return_value = db_instance
        yield db_instance

@pytest.fixture
def mock_quote_db_sql():
    with patch("art_studio_tz.cli.quote_db_sql") as mock:
        db_instance = MagicMock()
        mock.return_value.__enter__.return_value = db_instance
        yield db_instance

def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output.strip() == packet.__version__

def test_add(mock_quote_db):
    result = runner.invoke(app, ["add", "Hello", "world", "-a", "Author"])
    assert result.exit_code == 0
    mock_quote_db.add_quote.assert_called_once()
    # Проверка аргументов
    arg = mock_quote_db.add_quote.call_args[0][0]
    assert arg.text == "Hello world"
    assert arg.author == "Author"

def test_delete_valid(mock_quote_db):
    result = runner.invoke(app, ["delete", "1"])
    assert result.exit_code == 0
    mock_quote_db.delete_quote.assert_called_once_with(1)

def test_delete_invalid(mock_quote_db):
    mock_quote_db.delete_quote.side_effect = InvalidQuoteId
    result = runner.invoke(app, ["delete", "1"])
    assert result.exit_code == 0
    assert "Error" in result.output

def test_list_quote(mock_quote_db):
    quote = MagicMock()
    quote.id = 1
    quote.timestep = "2025-01-01"
    quote.text = "Hello"
    quote.author = "Author"
    mock_quote_db.list_quote.return_value = [quote]

    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Hello" in result.output
    assert "Author" in result.output

def test_update(mock_quote_db):
    result = runner.invoke(app, ["update", "1", "-t", "New text", "-o", "New author"])
    assert result.exit_code == 0
    mock_quote_db.update_quote.assert_called_once()
    arg = mock_quote_db.update_quote.call_args[0][1]
    assert arg.text == "New text"
    assert arg.author == "New author"

def test_start(mock_quote_db):
    result = runner.invoke(app, ["start", "-p", "0"])
    assert result.exit_code == 0
    mock_quote_db.start.assert_called_once()

def test_sql_get(mock_quote_db_sql):
    result = runner.invoke(app, ["get", "-u", "user", "-p", "pass"])
    assert result.exit_code == 0
    mock_quote_db_sql.get_some_quotes.assert_called_once()

@pytest.mark.skip()
def test_sql_delete_all(mock_quote_db_sql):
    mock_quote_db_sql.delete_all.return_value = None  

    result = runner.invoke(
        app,
        [
            "delete_all_sql",
            "--user", "user",
            "--password", "pass",
            "--host", "localhost",
            "--port", "3306",
            "--database", "quotes_db"
        ],
        standalone_mode=False
    )

    print(result.output)  
    assert result.exit_code == 0
    mock_quote_db_sql.delete_all.assert_called_once()

@pytest.mark.skip()
def test_sql_list_latest_5(mock_quote_db_sql):
    class FakeQuote:
        def __init__(self):
            self.id = 1
            self.timestep = "2025-01-01"
            self.text = "Hello"
            self.author = "Author"

    mock_quote_db_sql.get_latest.return_value = [FakeQuote()]

    result = runner.invoke(app, ["list_latest_5", "-u", "user", "-p", "pass"])
    assert result.exit_code == 0
    assert "Hello" in result.output
    assert "Author" in result.output

def test_config(mock_quote_db):
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    mock_quote_db.path.assert_called_once()

def test_count(mock_quote_db):
    mock_quote_db.count.return_value = 42
    result = runner.invoke(app, ["count"])
    assert result.exit_code == 0
    assert "42" in result.output
