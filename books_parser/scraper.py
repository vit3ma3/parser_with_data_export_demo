"""Обход сайта: категории -> страницы пагинации -> карточки книг."""

import logging

from . import config
from .http import PoliteSession
from .parser import Book, parse_book, parse_book_links, parse_categories, parse_next_page

log = logging.getLogger(__name__)


def get_categories(session: PoliteSession) -> dict[str, str]:
    return parse_categories(session.get(config.BASE_URL), config.BASE_URL)


def scrape_category(
    session: PoliteSession, name: str, url: str, max_pages: int | None = None
) -> list[Book]:
    books: list[Book] = []
    page_url: str | None = url
    page = 0
    while page_url and (max_pages is None or page < max_pages):
        page += 1
        html = session.get(page_url)
        links = parse_book_links(html, page_url)
        log.info("[%s] страница %d: %d книг", name, page, len(links))
        for link in links:
            try:
                books.append(parse_book(session.get(link), link, category=name))
            except Exception as exc:  # одна битая карточка не должна ронять весь обход
                log.error("Не удалось разобрать %s: %s", link, exc)
        page_url = parse_next_page(html, page_url)
    return books


def scrape(
    session: PoliteSession, category: str | None = None, max_pages: int | None = None
) -> list[Book]:
    categories = get_categories(session)
    log.info("Найдено категорий: %d", len(categories))
    if category:
        matched = {k: v for k, v in categories.items() if k.lower() == category.lower()}
        if not matched:
            raise SystemExit(
                f"Категория {category!r} не найдена. Доступные: {', '.join(sorted(categories))}"
            )
        categories = matched

    books: list[Book] = []
    for i, (name, url) in enumerate(categories.items(), 1):
        log.info("Категория %d/%d: %s", i, len(categories), name)
        books.extend(scrape_category(session, name, url, max_pages))
    log.info("Всего собрано книг: %d", len(books))
    return books
