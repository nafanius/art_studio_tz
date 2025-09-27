"""
DB for the quotes project
"""
import csv
from pathlib import Path
from typing import Any

class DB:
    def __init__(self, db_path: Path, db_file_prefix: str, fieldnames: list[str]):
        """
        fieldnames — список колонок, которые будут храниться в CSV
        """
        self.file = db_path / f"{db_file_prefix}.csv"
        self.fieldnames = ['id', *fieldnames]  # первая колонка — id
        if not self.file.exists():
            self.file.parent.mkdir(parents=True, exist_ok=True)
            with self.file.open('w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def _read_all_rows(self) -> list[dict[str, Any]]:
        rows = []
        with self.file.open('r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            return rows

    def create(self, item: dict[str, Any]) -> int:
        rows = self._read_all_rows()
        if rows == []:
            new_id = 1
        else:    
            new_id = max([int(r['id']) for r in rows], default=0) + 1
        row = {**item, 'id': new_id}
        with self.file.open('a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(row)
        print(new_id)
        return new_id

    def read(self, id: int) -> dict[str, Any] | None:
        rows = self._read_all_rows()
        for r in rows:
            if int(r['id']) == id:
                return r
        return None

    def read_all(self) -> list[dict[str, Any]]:
        return self._read_all_rows()

    def update(self, id: int, mods: dict[str, Any]) -> None:
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
        rows = [r for r in self._read_all_rows() if int(r['id']) != id]
        with self.file.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def delete_all(self) -> None:
        with self.file.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()  

    def count(self) -> int:
        return len(self._read_all_rows())