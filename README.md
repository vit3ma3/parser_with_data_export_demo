# Парсер каталога с выгрузкой в Excel / Google Sheets

Демо-проект для портфолио: парсер учебного сайта [books.toscrape.com](https://books.toscrape.com)
(создан специально для практики парсинга) с выгрузкой в оформленный Excel-отчёт
и, опционально, в Google Таблицу.

## Что собирается

По каждой книге: название, категория, цена (числом), рейтинг (1–5), наличие,
количество на складе, ссылка.

Excel-файл готов для передачи заказчику:

- лист **«Книги»** — жирная шапка, автофильтр, закреплённая первая строка,
  ширина колонок по содержимому, цены в числовом формате, кликабельные ссылки;
- лист **«Сводка по категориям»** — количество книг, средняя цена, средний рейтинг.

Пример результата: [`examples/sample_mystery.xlsx`](examples/sample_mystery.xlsx).

## Возможности

- обход всех категорий и всех страниц пагинации;
- вежливый парсинг: задержка между запросами, повторы при ошибках сети и 429/5xx
  с экспоненциальной паузой, собственный User-Agent;
- лог прогресса в консоль;
- все CSS-селекторы и сетевые настройки вынесены в
  [`books_parser/config.py`](books_parser/config.py) — для адаптации под другой
  сайт обычно достаточно поменять их;
- тесты разбора HTML на сохранённых страницах.

## Установка

Нужен Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Примеры запуска

```bash
# весь каталог (≈1000 книг, ~10 минут из-за задержки между запросами)
python main.py

# одна категория
python main.py --category Travel --out travel.xlsx

# по одной странице пагинации в каждой категории — быстрый пробный прогон
python main.py --max-pages 1 --out preview.xlsx

# свой интервал между запросами и подробный лог
python main.py --category Mystery --delay 1 -v
```

| Аргумент | Описание |
|---|---|
| `--category` | название категории (без учёта регистра); по умолчанию — все |
| `--max-pages` | максимум страниц пагинации на категорию |
| `--out` | имя Excel-файла (по умолчанию `books.xlsx`) |
| `--delay` | задержка между запросами, сек (по умолчанию 0.5) |
| `--gsheets` | дополнительно выгрузить в Google Таблицу |
| `--credentials` | путь к JSON-ключу сервисного аккаунта (по умолчанию `service_account.json`) |
| `--sheet` | URL или ключ Google Таблицы |
| `-v` | подробный лог |

Пример вывода:

```
18:22:20 INFO    Найдено категорий: 50
18:22:20 INFO    Категория 1/1: Mystery
18:22:21 INFO    [Mystery] страница 1: 20 книг
18:22:25 INFO    [Mystery] страница 2: 12 книг
18:22:27 INFO    Всего собрано книг: 32
18:22:27 INFO    Excel сохранён: mystery.xlsx
```

## Выгрузка в Google Таблицу

```bash
python main.py --category Travel --gsheets \
    --credentials service_account.json \
    --sheet "https://docs.google.com/spreadsheets/d/<ID>/edit"
```

Будут созданы (или перезаписаны) листы «Книги» и «Сводка по категориям».

### Как получить ключ сервисного аккаунта

1. Откройте [Google Cloud Console](https://console.cloud.google.com/) и создайте
   проект (или выберите существующий).
2. В разделе **APIs & Services → Library** включите **Google Sheets API**
   и **Google Drive API**.
3. **APIs & Services → Credentials → Create credentials → Service account**.
   Задайте имя, роли можно не назначать.
4. Откройте созданный сервисный аккаунт → вкладка **Keys → Add key → Create new key → JSON**.
   Скачанный файл сохраните в папку проекта как `service_account.json`
   (он уже в `.gitignore` — не публикуйте его).
5. Создайте Google Таблицу и нажмите **«Настройки доступа»**: добавьте email
   сервисного аккаунта (поле `client_email` в JSON, вида
   `name@project.iam.gserviceaccount.com`) с правами **Редактор**.
6. Передайте URL таблицы в `--sheet`.

## Тесты

```bash
pytest -q
```

Тесты проверяют разбор категорий, списка книг, пагинации и карточки книги на
HTML-страницах, сохранённых в `tests/fixtures/`.

## Структура

```
books_parser/
├── config.py          # URL, задержки, ретраи, User-Agent, CSS-селекторы
├── http.py            # HTTP-сессия: задержка, повторы, User-Agent
├── parser.py          # разбор HTML (чистые функции)
├── scraper.py         # обход категорий и пагинации
├── export_excel.py    # оформленный Excel + сводка
├── export_gsheets.py  # выгрузка в Google Sheets (gspread)
└── cli.py             # аргументы командной строки
tests/
├── fixtures/          # сохранённые HTML-страницы
└── test_parser.py
main.py                # точка входа
```
