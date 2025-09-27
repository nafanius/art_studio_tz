"""
API for the quets project
"""
import requests                                                                                                                                                                                                   
import time, os
from datetime import datetime, timezone
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path


from .db import DB

__all__ = [
    "Quote",
    "QuoteDB",
    "QuoteException",
    "MissingText",
    "InvalidQuoteId",
    "BadReqest",
]

@dataclass
class Quote:
    text: str = None
    author: str = None
    timestep: str = None 
    id: int = field(default=None, compare=False)

    @classmethod
    def from_dict(cls, d):
        return Quote(**d)
    def to_dict(self):
        return asdict(self)


class QuoteException(Exception):
    pass


class MissingText(QuoteException):
    pass


class InvalidQuoteId(QuoteException):
    pass

class BadReqest(QuoteException):
    pass


class QuoteDB:
    def __init__(self, db_path):
        self._db_path = db_path
        self._db = DB(db_path, "quotes", ["timestep",'text', 'author'])

    def add_quote(self, quote: Quote) -> int:
        """Add a quote, return the id of quote."""
        if not quote.text:
            raise MissingText
        if quote.author is None:
            quote.author = ""
        id = self._db.create(quote.to_dict())
        self._db.update(id, {"id": id,
                             "timestep":datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z') })
        return id

    def get_quote(self, quote_id: int) -> Quote:
        """Return a quote with a matching id."""
        db_item = self._db.read(quote_id)
        if db_item is not None:
            return Quote.from_dict(db_item)
        else:
            raise InvalidQuoteId(quote_id)

    def list_quote(self, author=None):
        """Return a list of quotes."""
        all = self._db.read_all()
        if author is not None:
            return [
                Quote.from_dict(t)
                for t in all
                if (t["author"] == author)
            ]
        else:
            return [Quote.from_dict(t) for t in all]

    def count(self) -> int:
        """Return the number of quotes in db."""
        return self._db.count()

    def update_qote(self, quote_id: int, quote_mods: Quote) -> None:
        """Update a quote with modifications."""
        try:
            self._db.update(quote_id, quote_mods.to_dict())
        except KeyError as exc:
            raise InvalidQuoteId(quote_id) from exc
        
    def start(self, url: str, pause: float):
        """Set a quote state to 'in prog'."""


        # url = "https://zenquotes.io/api/random"    
                                                                                                                                                                           
        print("For stop taking quotes press 'Ctrl + C'") 
                                                                                                                                                                                                                   
        while True:                                                                                                                                                                                                   
            try:                                                                                                                                                                                                      
                response = requests.get(url)                                                                                                                                                                          
                response.raise_for_status()  # Генерирует исключение для статуса ошибки HTTP                                                                                                                          
                data = response.json()                                                                                                                                                                                
                                                                                                                                                                                                                    
                if data:                                                                                                                                                                                              
                    quote = data[0]["q"]                                                                                                                                                                              
                    author = data[0]["a"]
                    self.add_quote(Quote(text=quote, author=author))                                                                                                                                                                             
                    print(f"Added Quote: {quote} - Author: {author}")                                                                                                                                                       
                else:                                                                                                                                                                                                 
                    print("No data received.")
                print("For stop taking quotes press 'Ctrl + C'")                                                                                                                                                                        
                time.sleep(pause)  # Пауза в 1 секунду

            except requests.exceptions.RequestException as e:                                                                                                                                                         
                print(f"Error fetching quote: {e}")                                                                                                                                                                   

            except KeyboardInterrupt:                                                                                                                                                                                     
                print("\nОстановка запроса цитат пользователем.")
                break   


    def delete_quote(self, quote_id: int) -> None:
        """Remove a quote from db with given quote_id."""
        try:
            self._db.delete(quote_id)
        except KeyError as exc:
            raise InvalidQuoteId(quote_id) from exc

    def delete_all(self) -> None:
        """Remove all quotes from db."""
        self._db.delete_all()

    def path(self):
        return self._db_path


if __name__ == "__main__":
    ob = QuoteDB(Path(os.getcwd()))
    # ob.start("https://zenquotes.io/api/random",10)
    print(ob.list_quote())
    print(ob.count())
    # ob.delete_all()

    ob.delete_quote(1)
    ob.update_qote(2, Quote(text="New text"))
    print(ob.get_quote(2))
    ob.add_quote(Quote(text="Some text", author="Some author"))
    print(ob.list_quote())  
    print(ob.count())
    ob.delete_all()      

