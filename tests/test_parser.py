from pathlib import Path

import pytest

from books_parser import parser

FIXTURES = Path(__file__).parent / "fixtures"
BASE = "https://books.toscrape.com/"


def load(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def test_parse_categories():
    cats = parser.parse_categories(load("index.html"), BASE + "index.html")
    assert len(cats) == 50
    assert "Books" not in cats  # корневая категория не попадает в список
    assert cats["Travel"] == BASE + "catalogue/category/books/travel_2/index.html"


def test_parse_book_links_and_next_page():
    url = BASE + "catalogue/category/books/mystery_3/index.html"
    html = load("category_mystery_p1.html")
    links = parser.parse_book_links(html, url)
    assert len(links) == 20
    assert links[0] == BASE + "catalogue/sharp-objects_997/index.html"
    assert parser.parse_next_page(html, url) == BASE + "catalogue/category/books/mystery_3/page-2.html"


def test_no_next_page_on_single_page_category():
    url = BASE + "catalogue/category/books/travel_2/index.html"
    html = load("category_travel.html")
    assert len(parser.parse_book_links(html, url)) == 11
    assert parser.parse_next_page(html, url) is None


def test_parse_book_detail():
    url = BASE + "catalogue/a-light-in-the-attic_1000/index.html"
    book = parser.parse_book(load("book_detail.html"), url)
    assert book == parser.Book(
        title="A Light in the Attic",
        category="Poetry",
        price=51.77,
        rating=3,
        in_stock=True,
        stock_qty=22,
        url=url,
    )


@pytest.mark.parametrize("text, expected", [
    ("£51.77", 51.77),
    ("Â£13.99", 13.99),
])
def test_parse_price(text, expected):
    assert parser.parse_price(text) == expected


@pytest.mark.parametrize("text, expected", [
    ("In stock (22 available)", (True, 22)),
    ("Out of stock", (False, 0)),
])
def test_parse_availability(text, expected):
    assert parser.parse_availability(text) == expected
