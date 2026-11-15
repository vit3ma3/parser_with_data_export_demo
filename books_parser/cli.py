import argparse
import logging

from .export_excel import export_excel
from .http import PoliteSession
from .scraper import scrape


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Парсер каталога books.toscrape.com с выгрузкой в Excel")
    p.add_argument("--category", help="название категории (по умолчанию — все), напр. 'Travel'")
    p.add_argument("--max-pages", type=int, help="максимум страниц пагинации на категорию")
    p.add_argument("--out", default="books.xlsx", help="имя Excel-файла (по умолчанию books.xlsx)")
    p.add_argument("--delay", type=float, default=None, help="задержка между запросами, сек")
    p.add_argument("--gsheets", action="store_true", help="дополнительно выгрузить в Google Таблицу")
    p.add_argument("--credentials", default="service_account.json",
                   help="JSON-ключ сервисного аккаунта (для --gsheets)")
    p.add_argument("--sheet", help="URL или ключ Google Таблицы (для --gsheets)")
    p.add_argument("-v", "--verbose", action="store_true", help="подробный лог")
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.gsheets and not args.sheet:
        raise SystemExit("Для --gsheets укажите --sheet (URL или ключ таблицы)")
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )
    log = logging.getLogger("books_parser")

    session = PoliteSession() if args.delay is None else PoliteSession(delay=args.delay)
    books = scrape(session, category=args.category, max_pages=args.max_pages)

    export_excel(books, args.out)
    log.info("Excel сохранён: %s", args.out)

    if args.gsheets:
        from .export_gsheets import export_gsheets
        export_gsheets(books, args.credentials, args.sheet)
