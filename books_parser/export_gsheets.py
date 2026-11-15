"""Опциональная выгрузка в Google Таблицу через сервисный аккаунт (gspread)."""

import logging

from .export_excel import BOOK_HEADERS, SUMMARY_HEADERS, summarize
from .parser import Book

log = logging.getLogger(__name__)


def export_gsheets(books: list[Book], credentials_path: str, spreadsheet: str) -> str:
    """spreadsheet — ключ или URL существующей таблицы, открытой для сервисного аккаунта."""
    import gspread  # импорт здесь, чтобы gspread был нужен только с флагом --gsheets

    gc = gspread.service_account(filename=credentials_path)
    sh = gc.open_by_url(spreadsheet) if spreadsheet.startswith("http") else gc.open_by_key(spreadsheet)

    def write(title: str, rows: list[list]) -> None:
        try:
            ws = sh.worksheet(title)
            ws.clear()
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title=title, rows=len(rows) + 10, cols=len(rows[0]))
        ws.update(rows, "A1")
        ws.format("1:1", {"textFormat": {"bold": True}})
        ws.freeze(rows=1)
        ws.set_basic_filter()

    write("Книги", [BOOK_HEADERS] + [
        [b.title, b.category, b.price, b.rating, "Да" if b.in_stock else "Нет", b.stock_qty, b.url]
        for b in books
    ])
    write("Сводка по категориям", [SUMMARY_HEADERS] + [list(r) for r in summarize(books)])
    log.info("Данные выгружены в Google Таблицу: %s", sh.url)
    return sh.url
