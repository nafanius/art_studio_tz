## Art studio tz CLI

Это консольное приложение для управления цитатами.
Поддерживает локальную базу данных(quotes.csv) и работу с MySQL.

- решение ТЗ пункт(3, 4, 5)

- решение ТЗ пункт(2) index.html: [Мудрые цитаты](https://nafanius.github.io/art_studio_tz/)

- Репозиторий: [https://github.com/nafanius/art_studio_tz](https://github.com/nafanius/art_studio_tz)
- Лицензия: MIT

## Возможности

- Получение цитат из внешнего API с паузой по одной или блоками по 50 шт(`zenquotes.io`).
- Добавление, удаление, обновление цитат.
- Список цитат с фильтрацией по автору, по дате добаления в БД.
- Сохранение и управления цитатами в локальную БД(quotes.csv) или MySQL.
- Получение свежих цитат из БД MySQL.
- Работа через современный CLI-фреймворк [Typer](https://typer.tiangolo.com) и форматирование таблиц с помощью [Rich](https://github.com/Textualize/rich).

## Установка

**С PyPI (рекомендуется)**

```bash
pip install art_studio_tz
```

**Из GitHub**

```bash
pip install git+https://github.com/nafanius/art_studio_tz.git
```

**Из исходного кода**

```bash
# Клонируем репозиторий
git clone https://github.com/nafanius/art_studio_tz.git
cd art_studio_tz

# Устанавливаем через pip
pip install .

# Или с помощью poetry (для разработки)
poetry install
```

## Использование

**После установки доступна команда art_studio_tz:**

```bash
art_studio_tz --help
```

**Основные команды CLI для локальной БД(quotes.csv)**

- `start [-u URL] [-p Пауза]` — Получать цитаты с API и сохранять в локальную БД(quotes.csv) с паузой между запросами (по умолчанию 5 с)
- `list [-a Автор]` — Показать список цитат (опционально с фильтрацией по автору)
- `version` — Показать версию приложения
- `add "ТЕКСТ" -a "Автор"` — Добавить цитату в локальную БД
- `delete <ID>` — Удалить цитату по ID, либо все
- `update <ID> -t "Новый текст" -o "Новый автор"` — Обновить цитату по ID
- `config` — Показать путь к локальной базе данных
- `count` — Показать количество цитат в локальной базе

**Команды для работы с MySQL**

- `get -u user -p password [-H host] [-P port] [-d db] [--url URL]` — Получить 50 цитат из API и записать в MySQL(требуется сервер mySQL)
- `list-latest-5 -u user -p pass ... [-n N]` — Показать последние N цитат из MySQL (по умолчанию 5)
  --отробатывает через ORM аналогичено сырому запросу:

  ```SQL
    SELECT id, text
    FROM quotes
    ORDER BY timestep DESC, id DESC
    LIMIT 5;
  ```

- `delete-all-sql -u user -p pass ...` — Удалить все цитаты в MySQL
- `list-sql -u user -p pass ... [-a Автор]` — Показать список цитат из MySQL

  **каждая команда имеет отдельный --help пример:**

```bash
  art_studio_tz get --help

  $ art_studio_tz get -u USER -p PASSWORD

    Usage: art_studio_tz get [OPTIONS]


  Get 50 quotes from url and add to mySQL


  * --user -u TEXT Database user [required]
  * --password -p TEXT Database password [required]
  --host -H TEXT Database host, default localhost
  --port -P INTEGER Database port, default 3306
  --database -d TEXT Database name, default quotes_db
  --url TEXT URL for get quotes, default https://zenquotes.io/api/random
  --help Show this message and exit.
```

**Переменные окружения**

```bash
  export QUOTES_DB_DIR=/путь/к/папке
```

**Разработка и тестирование**

```bash
poetry install --with test
pytest
```

## Требования

- Python >= 3.10
- Зависимости перечислены в pyproject.toml (SQLAlchemy, Typer, Rich и др.), requirement.txt

## Струуктура

```bash
.
├── art_studio_tz
│ ├── __init__.py
│ ├── __main__.py
│ ├── cli.py          # UI через командную строку
│ ├── api.py          # API управляющее приложением сязь между CLI и DB
│ ├── db.py           # БД на базе csv
│ └── db_sql.py       # БД на базе MySQL
├── index.html        # Страница цитатник
├── LICENSE
├── pyproject.toml
├── quotes.csv
├── README.md
├── requirement.txt
├── tests
│ ├── test_api.py
│ ├── test_cli.py
│ ├── test_db.py
│ └── test_db_sql.py
└── ТЗ.pdf
```

## Лицензия

MIT © 2025 Ilin Maksim
