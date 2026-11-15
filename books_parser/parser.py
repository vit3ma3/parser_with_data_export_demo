"""Разбор HTML. Чистые функции без сетевых запросов — их удобно тестировать."""

import re
from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .config import RATING_WORDS, SELECTORS


@dataclass
class Book:
    title: str
    category: str
    price: float
    rating: int
    in_stock: bool
    stock_qty: int
    url: str


def make_soup(html: bytes | str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def parse_categories(html: bytes | str, page_url: str) -> dict[str, str]:
    """{название категории: абсолютный URL}."""
    soup = make_soup(html)
    return {
        a.get_text(strip=True): urljoin(page_url, a["href"])
        for a in soup.select(SELECTORS["category_links"])
    }


def parse_book_links(html: bytes | str, page_url: str) -> list[str]:
    soup = make_soup(html)
    return [urljoin(page_url, a["href"]) for a in soup.select(SELECTORS["book_links"])]


def parse_next_page(html: bytes | str, page_url: str) -> str | None:
    link = make_soup(html).select_one(SELECTORS["next_page"])
    return urljoin(page_url, link["href"]) if link else None


def parse_price(text: str) -> float:
    match = re.search(r"\d+(?:[.,]\d+)?", text)
    if not match:
        raise ValueError(f"Не удалось разобрать цену: {text!r}")
    return float(match.group().replace(",", "."))


def parse_rating(classes: list[str]) -> int:
    for cls in classes:
        if cls in RATING_WORDS:
            return RATING_WORDS[cls]
    return 0


def parse_availability(text: str) -> tuple[bool, int]:
    """'In stock (22 available)' -> (True, 22)."""
    in_stock = "in stock" in text.lower()
    match = re.search(r"(\d+)\s+available", text)
    return in_stock, int(match.group(1)) if match else 0


def parse_book(html: bytes | str, url: str, category: str | None = None) -> Book:
    soup = make_soup(html)
    if category is None:
        crumb = soup.select_one(SELECTORS["breadcrumb_category"])
        category = crumb.get_text(strip=True) if crumb else ""
    in_stock, qty = parse_availability(soup.select_one(SELECTORS["availability"]).get_text())
    return Book(
        title=soup.select_one(SELECTORS["title"]).get_text(strip=True),
        category=category,
        price=parse_price(soup.select_one(SELECTORS["price"]).get_text()),
        rating=parse_rating(soup.select_one(SELECTORS["rating"]).get("class", [])),
        in_stock=in_stock,
        stock_qty=qty,
        url=url,
    )
