"""Command Line Interface (CLI) for quotes project."""
import os
from io import StringIO
import pathlib
import rich
from rich.table import Table
from contextlib import contextmanager
from typing import List

import app_quote

import typer



app = typer.Typer(add_completion=True)


@app.command()
def version():
    """Return version of app_quote application"""
    print(app_quote.__version__)


@app.command()
def add(
    text: List[str],
    author: str = typer.Option(None, "-a", "--author", help="Author quote")
):
    """Add a quote to db."""
    text = " ".join(text) if text else None
    with quote_db() as db:
        db.add_quote(app_quote.Quote(text=text, author=author))


@app.command()
def delete(quote_id: int):
    """Remove quote in db with given id."""
    with quote_db() as db:
        try:
            db.delete_quote(quote_id)
        except app_quote.InvalidQuoteId:
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
                quote_id, app_quote.Quote(text=text, author=author)
            )
        except app_quote.InvalidQuoteId:
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
        except app_quote.BadReqest:
            print(f"Could not get quote from {url}")

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
    db_path = get_path()
    db = app_quote.QuoteDB(db_path)
    yield db

