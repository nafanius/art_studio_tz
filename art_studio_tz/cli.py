"""Command Line Interface (CLI) for quotes project."""
import os
from io import StringIO
import pathlib
import rich
from rich.table import Table
from contextlib import contextmanager
from typing import List

import art_studio_tz

import typer



app = typer.Typer(add_completion=True)


@app.command()
def version():
    """Return version of app_quote application"""
    print(art_studio_tz.__version__)


@app.command()
def add(
    text: List[str],
    author: str = typer.Option(None, "-a", "--author", help="Author quote")
):
    """Add a quote to db."""
    text = " ".join(text) if text else None
    with quote_db() as db:
        db.add_quote(art_studio_tz.Quote(text=text, author=author))


@app.command()
def delete(quote_id: int):
    """Remove quote in db with given id."""
    with quote_db() as db:
        try:
            db.delete_quote(quote_id)
        except art_studio_tz.InvalidQuoteId:
            print(f"Error: Invalid qupte id {quote_id}")


@app.command("list")
def list_quote(
    author: str = typer.Option(None, "-a", "--author", help="sort for author")
):
    """
    List quotes in db.
    """
    with quote_db() as db:
        the_quote = db.list_quote(author=author)
        table = Table(box=rich.box.SIMPLE)
        table.add_column("ID")
        table.add_column("TimeStep")
        table.add_column("Quote")
        table.add_column("Author")
        for t in the_quote:
            author = "" if t.author is None else t.author
            table.add_row(str(t.id),t.timestep, t.text, author)
        out = StringIO()
        rich.print(table, file=out)
        print(out.getvalue())


@app.command()
def update(
    quote_id: int,
    author: str = typer.Option(None, "-o", "--owner"),
    text: List[str] = typer.Option(None, "-t", "--text"),
):
    """Modify a quote in db with given id with new info."""
    text = " ".join(text) if text else None
    with quote_db() as db:
        try:
            db.update_qote(
                quote_id, art_studio_tz.Quote(text=text, author=author)
            )
        except art_studio_tz.InvalidQuoteId:
            print(f"Error: Invalid quote id {quote_id}")


@app.command()
def start(url: str = typer.Option("https://zenquotes.io/api/random", "-u", "--url", help="URL for get quotes, default https://zenquotes.io/api/random"),
          pause: float = typer.Option(5, "-p", "--pause", help="pause between requests quotes in seconds, default 5 seconds")):
    """Get quote from url and add to db. with pause between requests.
    url - URL for get quotes, default https://zenquotes.io/api/random
    pause - pause between requests quotes in seconds, default 5 seconds"""
    with quote_db() as db:
        try:
            db.start(url, pause)
        except art_studio_tz.BadReqest:
            print(f"Could not get quote from {url}")

@app.command()
def get(user: str = typer.Option(..., "-u", "--user", help="Database user"),
        password: str = typer.Option(..., "-p", "--password", help="Database password"),
        host: str = typer.Option("localhost", "-H", "--host", help="Database host, default localhost"),
        port: int = typer.Option(3306, "-P", "--port", help="Database port, default 3306"),
        database: str = typer.Option("quotes_db", "-d", "--database", help="Database name, default quotes_db"),
        url: str = typer.Option("https://zenquotes.io/api/quotes", "--url", help="URL for get quotes, default https://zenquotes.io/api/random"),
          ):
    """Get 50 quotes from url and add to mySQL"""
    with quote_db_sql(user=user, password=password, host=host, port=port, database=database) as db_sql:
        try:
            db_sql.get_some_quotes(url)
        except art_studio_tz.BadReqest:
            print(f"Could not get quote from {url}")

@app.command()
def delete_all_sql(user: str = typer.Option(..., "-u", "--user", help="Database user"),
        password: str = typer.Option(..., "-p", "--password", help="Database password"),
        host: str = typer.Option("localhost", "-H", "--host", help="Database host, default localhost"),
        port: int = typer.Option(3306, "-P", "--port", help="Database port, default 3306"),
        database: str = typer.Option("quotes_db", "-d", "--database", help="Database name, default quotes_db"),
        ):
    """Delete all quotes in mySQL"""
    with quote_db_sql(user=user, password=password, host=host, port=port, database=database) as db_sql:
        try:
            db_sql.delete_all() 
        except Exception as err:
            print(f"Could not delete quotes in {database} because {err}")
        
@app.command()
def list_sql(
    user: str = typer.Option(..., "-u", "--user", help="Database user"),
    password: str = typer.Option(..., "-p", "--password", help="Database password"),
    host: str = typer.Option("localhost", "-H", "--host", help="Database host, default localhost"),
    port: int = typer.Option(3306, "-P", "--port", help="Database port, default 3306"),
    database: str = typer.Option("quotes_db", "-d", "--database", help="Database name, default quotes_db"),
    author: str = typer.Option(None, "-a", "--author", help="sort for author")
):
    """
    List quotes in mySQL
    """
    with quote_db_sql(user=user, password=password, host=host, port=port, database=database) as db_sql:
        the_quote = db_sql.list_quote(author=author)
        table = Table(box=rich.box.SIMPLE)
        table.add_column("ID")
        table.add_column("TimeStep")
        table.add_column("Quote")
        table.add_column("Author")
        for t in the_quote:
            author = "" if t.author is None else t.author
            table.add_row(str(t.id), str(t.timestep), t.text, author)
        out = StringIO()
        rich.print(table, file=out)
        print(out.getvalue())

@app.command()
def list_latest_5(
    user: str = typer.Option(..., "-u", "--user", help="Database user"),
    password: str = typer.Option(..., "-p", "--password", help="Database password"),
    host: str = typer.Option("localhost", "-H", "--host", help="Database host, default localhost"),
    port: int = typer.Option(3306, "-P", "--port", help="Database port, default 3306"),
    database: str = typer.Option("quotes_db", "-d", "--database", help="Database name, default quotes_db"),
    number: int = typer.Option(5, "-n", "--number", help="Number of latest quotes to list, default 5")
):
    """
    list latest 'number' quotes in mySQL, default 5
    """
    with quote_db_sql(user=user, password=password, host=host, port=port, database=database) as db_sql:
        the_quote = db_sql.get_latest(number)
        table = Table(box=rich.box.SIMPLE)
        table.add_column("ID")
        table.add_column("TimeStep")
        table.add_column("Quote")
        table.add_column("Author")
        for t in the_quote:
            author = "" if t.author is None else t.author
            table.add_row(str(t.id), str(t.timestep), t.text, author)
        out = StringIO()
        rich.print(table, file=out)
        print(out.getvalue())

@app.command()
def config():
    """List the path to the quotes db."""
    with quote_db() as db:
        print(db.path())


@app.command()
def count():
    """Return number of quotes in db."""
    with quote_db() as db:
        print(db.count())




@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    quotes is a small command line task tracking application.
    """
    if ctx.invoked_subcommand is None:
        list_quote(author=None)


def get_path():

    db_path_env = os.getenv("QUOTES_DB_DIR", "")
    if db_path_env:
        db_path = pathlib.Path(db_path_env)
    else:
        db_path = pathlib.Path(os.getcwd())
    return db_path


@contextmanager
def quote_db():
    """Context manager for QuoteDB.

    Yields:
        QuoteDB: QuoteDB instance
    """    
    db_path = get_path()
    db = art_studio_tz.QuoteDB(db_path)
    yield db

@contextmanager
def quote_db_sql(user: str, password: str, host: str, port: int, database: str):
    """
    Context manager for QuoteDBsql.

    Args:
        user (str): username for database
        password (str): password for database
        host (str): hostname for database
        port (int): port for database
        database (str): database name

    Yields:
        QuoteDBsql: QuoteDBsql instance
    """    
    db = art_studio_tz.QuoteDBsql(user=user, password=password, host=host, port=port, database=database)
    try:
        yield db
    finally:
        if hasattr(db, "engine") and isinstance(db.engine, Engine):
            db.engine.dispose()
        