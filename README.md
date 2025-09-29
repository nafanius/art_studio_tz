## Art studio tz CLI

[![Coverage](.github/badges/coverage.svg)](https://nafanius.github.io/art_studio_tz/docs/coverage_html_report/)
[![pages-build-deployment](https://github.com/nafanius/art_studio_tz/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/nafanius/art_studio_tz/actions/workflows/pages/pages-build-deployment)
[![Build Test Deploy](https://github.com/nafanius/art_studio_tz/actions/workflows/ci.yml/badge.svg)](https://github.com/nafanius/art_studio_tz/actions/workflows/ci.yml)

Это консольное приложение для управления цитатами.
Поддерживает локальную базу данных(quotes.csv) и работу с MySQL.

- решение ТЗ пункт(1) wordpress/random-quote.php: [[random_quote]](https://docs.google.com/document/d/e/2PACX-1vTVmd90XclSrG_l4o74Rf0JRaT1MMC-d-PRaWj0TgtXk9Rf5XEbkuses3ibg2i0XEgXnhr2H0y-sv_t/pub)
- решение ТЗ пункт(2) index.html: [Мудрые цитаты](https://nafanius.github.io/art_studio_tz/)
- решение ТЗ пункт(3, 4, 5): art_studio_tz - консольное приложенение работа с DB на основе CSV файла и MySQL c автоматической загрузкой данных по средсвам свободных API

- Репозиторий: [https://github.com/nafanius/art_studio_tz](https://github.com/nafanius/art_studio_tz)
- Лицензия: MIT

## Возможности

- Получение цитат из внешнего API с паузой по одной или блоками по 50 шт(`zenquotes.io`).
- Добавление, удаление, обновление цитат.
- Список цитат с фильтрацией по автору, по дате добаления в БД.
- Сохранение и управления цитатами в локальную БД(quotes.csv) или MySQL.
- Получение свежих цитат из БД MySQL c указанием количества (по умолчянию 5).
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
  $ art_studio_tz --help

  Usage: art_studio_tz [OPTIONS] COMMAND [ARGS]...

  quotes is a small command line task tracking application

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                           │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.    │
│ --help                        Show this message and exit.                                                         │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ version          Return version of app_quote application                                                          │
│ start            Get quote from url and add to db. with pause between requests. url - URL for get quotes, default │
│                  https://zenquotes.io/api/random pause - pause between requests quotes in seconds, default 5      │
│                  seconds                                                                                          │
│ list             List quotes in db.                                                                               │
│ add              Add a quote to db.                                                                               │
│ delete           Remove quote in db with given id.                                                                │
│ update           Modify a quote in db with given id with new info.                                                │
│ config           List the path to the quotes db.                                                                  │
│ count            Return number of quotes in db.                                                                   │
│ get              Get 50 quotes from url and add to mySQL                                                          │
│ list-sql         List quotes in mySQL                                                                             │
│ delete-all-sql   Delete all quotes in mySQL                                                                       │
│ list-latest-5    list latest 'number' quotes in mySQL, default 5                                                  │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

**Основные команды CLI для локальной БД(quotes.csv)**

- `start [-u URL] [-p Пауза]` — Получать цитаты с API и сохранять в локальную БД(quotes.csv) с паузой между запросами (по умолчанию 5 с)
- `list [-a Автор]` — Показать список цитат (опционально с фильтрацией по автору)
- `version` — Показать версию приложения
- `add "ТЕКСТ" -a "Автор"` — Добавить цитату в локальную БД
- `delete <ID>` — Удалить цитату по ID, либо все
- `update <ID> -t "Новый текст" -a "Новый автор"` — Обновить цитату по ID
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
$ art_studio_tz get --help

 Usage: art_studio_tz get [OPTIONS]

 Get 50 quotes from url and add to mySQL

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --user      -u      TEXT     Database user [required]                                          │
│ *  --password  -p      TEXT     Database password [required]                                      │
│    --host      -H      TEXT     Database host, default localhost [default: localhost]             │
│    --port      -P      INTEGER  Database port, default 3306 [default: 3306]                       │
│    --database  -d      TEXT     Database name, default quotes_db [default: quotes_db]             │
│    --url               TEXT     URL for get quotes, default https://zenquotes.io/api/quotes       │
│                                 [default: https://zenquotes.io/api/quotes]                        │
│    --help                       Show this message and exit.                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
```

**Примеры использования**

Получение цитаты каждые 30 секунд по API, запись в quotes.csv

```bash
  $ art_studio_tz start -p 30

  For stop taking quotes press 'Ctrl + C'
  Added Quote: The attempt to escape from pain, is what creates more pain. - Author: Gabor Mate
  For stop taking quotes press 'Ctrl + C'
  Added Quote: Our greatest glory is not in never falling but in rising every time we fall. - Author: Confucius
  For stop taking quotes press 'Ctrl + C'
  Added Quote: If the plan doesn't work, change the plan, but never the goal. - Author: Unknown
  For stop taking quotes press 'Ctrl + C'
  ^C
  Остановка запроса цитат пользователем.

```

Получение всех записей из quotes.csv

```bash
  $ art_studio_tz list

   ID   TimeStep                  Quote                                                                          Author
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  8    2025-09-28 08:31:24 UTC   The attempt to escape from pain, is what creates more pain.                    Gabor Mate
  9    2025-09-28 08:31:55 UTC   Our greatest glory is not in never falling but in rising every time we fall.   Confucius
  10   2025-09-28 08:32:26 UTC   If the plan doesn't work, change the plan, but never the goal.                 Unknown
```

Добавить 50 цитат в MySQL

```bash
  $ art_studio_tz get -u user -p pass --host 127.0.0.1 -d my_database

  Added Quote: Many answers to what you seek don't lie 'out there'. If you look inwards, you'll find the answer has been in you all along. Author: Celestine Chua
  Added Quote: Anyone who wants to achieve a dream must stay strong, focused and steady. - Author: Estee Lauder
  Added Quote: It's necessary to get the losers out of your life if you want to live your dream. - Author: Les Brown
  Added Quote: Mistake is a mistake only if you make it twice. - Author: Robin Sharma
  Added Quote: Not how long, but how well you have lived is the main thing. - Author: Seneca
  .....
```

Паказать 5 новейших цитат из MySQL

```bash
  $ art_studio_tz list-latest-5 -u user -p pass --host 127.0.0.1 -d my_database

  ID    TimeStep              Quote                                                              Author
 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  200   2025-09-28 11:02:33   To himself everyone is immortal; he may know that he is going to   Samuel Butler
                              die, but he can never know he is dead.
  198   2025-09-28 11:02:32   You just can't beat the person who never gives up.                 Babe Ruth
  199   2025-09-28 11:02:32   Art is the signature of civilizations.                             Beverly Sills
  196   2025-09-28 11:02:31   Love never keeps a man from pursuing his destiny.                  Paulo Coelho
  197   2025-09-28 11:02:31   Without the rain there would be no rainbow.                        Gilbert Chesterton

```

**Переменные окружения**

```bash
  # по умолчянию DB на основе CSV(quotes.csv) создаётся автомотически в директории откуда вызывается программа
  # при необходимости создайте переменную окружения где нужно сохранять quotes.csv
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

## Структура

```bash
.
├── art_studio_tz
│ ├── __init__.py
│ ├── __main__.py
│ ├── cli.py            # UI через командную строку
│ ├── api.py            # API управляющее приложением сdязь между CLI и DB
│ ├── db.py             # БД на базе csv
│ └── db_sql.py         # БД на базе MySQL
├── index.html          # Страница цитатник AJAX запросы
├── LICENSE
├── pyproject.toml
├── quotes.csv
├── README.md
├── requirement.txt
├── wordpress
│ └── random-quote.php  # Плагина Random Quotes для WordPress
├── tests
│ ├── test_api.py
│ ├── test_cli.py
│ ├── test_db.py
│ └── test_db_sql.py
└── ТЗ.pdf
```

## Лицензия

MIT © 2025 Ilin Maksim
