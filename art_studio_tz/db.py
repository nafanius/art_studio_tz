"""
DB for the quotes project
"""
import csv
from pathlib import Path
from typing import Any

class DB:
    """CSV file based DB class
    """
    def __init__(self, db_path: Path, db_file_prefix: str, fieldnames: list[str]):
        """initialize DB

        Args:
            db_path (Path): path to the db directory
            db_file_prefix (str): prefix for the db file name
            fieldnames (list[str]): list of field names (without 'id' field)
        """        
        self.file = db_path / f"{db_file_prefix}.csv"
        self.fieldnames = ['id', *fieldnames]  # первая колонка — id
        if not self.file.exists():
            self.file.parent.mkdir(parents=True, exist_ok=True)
            with self.file.open('w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def _read_all_rows(self) -> list[dict[str, Any]]:
        """read all rows from the CSV file

        Returns:
            list[dict[str, Any]]: list of dictionaries with row data
        """        
        rows = []
        with self.file.open('r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            return rows

    def create(self, item: dict[str, Any]) -> int:
        """create a new quote record

        Args:
            item (dict[str, Any]): dictionary with quote data

        Returns:
            int: new record id
        """        
        rows = self._read_all_rows()
        if rows == []:
            new_id = 1
        else:    
            new_id = max([int(r['id']) for r in rows], default=0) + 1
        row = {**item, 'id': new_id}
        with self.file.open('a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(row)
        return new_id

    def read(self, id: int) -> dict[str, Any] | None:
        """read a quote record by id

        Args:
            id (int): record id

        Returns:
            dict[str, Any] | None: dictionary with record data or None if not found
        """        
        rows = self._read_all_rows()
        for r in rows:
            if int(r['id']) == id:
                return r
        return None

    def read_all(self) -> list[dict[str, Any]]:
        """Read all quote records

        Returns:
            list[dict[str, Any]]: list of dictionary with quote data
        """        
        return self._read_all_rows()

    def update(self, id: int, mods: dict[str, Any]) -> None:
        """Update a quote record by id

        Args:
            id (int): id of the record to update
            mods (dict[str, Any]): dictionary with fields to update
        """        
        rows = self._read_all_rows()
        changed = False
        for r in rows:
            if int(r['id']) == id:
                for k, v in mods.items():
                    if v is not None and k in r:
                        r[k] = v
                changed = True
        if changed:
            with self.file.open('w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerows(rows)

    def delete(self, id: int) -> None:
        """Delete a quote record by id

        Args:
            id (int): id of the record to delete
        """        
        rows = [r for r in self._read_all_rows() if int(r['id']) != id]
        with self.file.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def delete_all(self) -> None:
        """Delete all quote records
        """
        with self.file.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()  

    def count(self) -> int:
        """Get number of records in the DB

        Returns:
            int: number of records
        """        
        return len(self._read_all_rows())