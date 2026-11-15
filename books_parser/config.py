"""Настройки парсера и CSS-селекторы.

Чтобы адаптировать парсер под другой сайт, обычно достаточно поменять
значения в этом файле.
"""

BASE_URL = "https://books.toscrape.com/"

# HTTP
USER_AGENT = "BooksParserDemo/1.0 (+https://github.com/vit3ma3/parser_with_data_export_demo)"
REQUEST_DELAY = 0.5  # секунд между запросами
TIMEOUT = 15  # секунд
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.0  # пауза перед повтором: 1с, 2с, 4с ...

# Селекторы
SELECTORS = {
    # главная страница: список категорий
    "category_links": "div.side_categories ul.nav-list > li > ul > li > a",
    # страница категории
    "book_links": "article.product_pod h3 a",
    "next_page": "ul.pager li.next a",
    # карточка книги
    "title": "div.product_main h1",
    "price": "div.product_main p.price_color",
    "rating": "div.product_main p.star-rating",
    "availability": "div.product_main p.availability",
    "breadcrumb_category": "ul.breadcrumb li:nth-last-of-type(2) a",
}

# Рейтинг задан классом: <p class="star-rating Three">
RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
