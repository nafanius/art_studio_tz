"""db_sql.py - SQLAlchemy based DB module"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, desc
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from typing import Any, Dict, List, Optional, Callable, cast

Base = declarative_base()


class QuoteModel(Base):
    """SQLAlchemy model for the quotes table."""
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(1024), nullable=False)
    author = Column(String(255), nullable=True)
    timestep = Column(DateTime(timezone=True), server_default=func.now())  # время создания записи

class DBsql:
    """SQLAlchemy based DB class
    """
    def __init__(self, user: str, password: str, host: str, port: int, database: str):
        db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        self.engine = create_engine(db_url, echo=False, future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _execute(self, func: Callable, commit: bool = True, default=None):
        """
        unified method to handle session lifecycle and errors
        """
        session = self.Session()
        try:
            result = func(session)
            if commit:
                session.commit()
            return result
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database error: {e}")
            return default
        finally:
            session.close()

    def create(self, item: Dict[str, Any]) -> Optional[int]:
        def _create(session):
            quote = QuoteModel(**item)
            session.add(quote)
            return quote.id
        return self._execute(_create)

    def read_all(self) -> List[Dict[str, Any]]:
        def _read_all(session):
            quotes = session.query(QuoteModel).all()
            return [{c.name: getattr(q, c.name) for c in q.__table__.columns} for q in quotes]
        return cast(List[Dict[str, Any]], self._execute(_read_all, commit=False, default=[]))

    def delete_all(self) -> bool:
        def _delete_all(session):
            session.query(QuoteModel).delete()
            return True
        return cast(bool, self._execute(_delete_all, default=False))

    def get_latest(self, n: int = 5) -> List[Dict[str, Any]]:
        def _latest(session):
            quotes = session.query(QuoteModel).order_by(desc(QuoteModel.timestep)).limit(n).all()
            return [{c.name: getattr(q, c.name) for c in q.__table__.columns} for q in quotes]
        return cast(List[Dict[str, Any]], self._execute(_latest, commit=False, default=[]))
