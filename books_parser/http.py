"""HTTP-клиент: свой User-Agent, задержка между запросами, повторы при ошибках."""

import logging
import time

import requests

from . import config

log = logging.getLogger(__name__)

RETRY_STATUSES = {429, 500, 502, 503, 504}


class PoliteSession:
    def __init__(
        self,
        delay: float = config.REQUEST_DELAY,
        retries: int = config.MAX_RETRIES,
        timeout: float = config.TIMEOUT,
    ):
        self.delay = delay
        self.retries = retries
        self.timeout = timeout
        self._last_request = 0.0
        self.session = requests.Session()
        self.session.headers["User-Agent"] = config.USER_AGENT

    def _wait(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request = time.monotonic()

    def get(self, url: str) -> bytes:
        """Возвращает тело ответа (bytes — кодировку определит BeautifulSoup)."""
        for attempt in range(1, self.retries + 1):
            self._wait()
            try:
                resp = self.session.get(url, timeout=self.timeout)
                if resp.status_code in RETRY_STATUSES:
                    raise requests.HTTPError(f"HTTP {resp.status_code}", response=resp)
                resp.raise_for_status()
                return resp.content
            except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as exc:
                status = getattr(exc.response, "status_code", None)
                if status is not None and status not in RETRY_STATUSES:
                    raise
                if attempt == self.retries:
                    raise
                pause = config.BACKOFF_FACTOR * 2 ** (attempt - 1)
                log.warning("Ошибка %s для %s, повтор %d/%d через %.0fс",
                            exc, url, attempt, self.retries - 1, pause)
                time.sleep(pause)
        raise AssertionError("unreachable")
