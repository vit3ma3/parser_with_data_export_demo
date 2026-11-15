"""Экспорт в Excel: лист с книгами + лист со сводкой по категориям."""

from collections import defaultdict

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from .parser import Book

BOOK_HEADERS = ["Название", "Категория", "Цена, £", "Рейтинг", "В наличии", "Кол-во на складе", "Ссылка"]
SUMMARY_HEADERS = ["Категория", "Кол-во книг", "Средняя цена, £", "Средний рейтинг"]

HEADER_FONT = Font(bold=True, color="FFFFFF")
HEADER_FILL = PatternFill("solid", fgColor="305496")
PRICE_FORMAT = "#,##0.00"
MAX_COL_WIDTH = 60


def summarize(books: list[Book]) -> list[tuple[str, int, float, float]]:
    groups: dict[str, list[Book]] = defaultdict(list)
    for b in books:
        groups[b.category].append(b)
    return [
        (
            cat,
            len(items),
            round(sum(b.price for b in items) / len(items), 2),
            round(sum(b.rating for b in items) / len(items), 2),
        )
        for cat, items in sorted(groups.items())
    ]


def _style_sheet(ws: Worksheet) -> None:
    for cell in ws[1]:
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for col in ws.columns:
        width = max(len(str(c.value)) if c.value is not None else 0 for c in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(width + 2, MAX_COL_WIDTH)


def export_excel(books: list[Book], path: str) -> None:
    wb = Workbook()

    ws = wb.active
    ws.title = "Книги"
    ws.append(BOOK_HEADERS)
    for b in books:
        ws.append([b.title, b.category, b.price, b.rating, "Да" if b.in_stock else "Нет", b.stock_qty, b.url])
        row = ws.max_row
        ws.cell(row, 3).number_format = PRICE_FORMAT
        link = ws.cell(row, 7)
        link.hyperlink = b.url
        link.style = "Hyperlink"
    _style_sheet(ws)

    ws2 = wb.create_sheet("Сводка по категориям")
    ws2.append(SUMMARY_HEADERS)
    for row in summarize(books):
        ws2.append(row)
        ws2.cell(ws2.max_row, 3).number_format = PRICE_FORMAT
        ws2.cell(ws2.max_row, 4).number_format = "0.00"
    _style_sheet(ws2)

    wb.save(path)
