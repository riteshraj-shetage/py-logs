"""
Web Scraper Module
==================
A lightweight, polite web scraper built on requests + BeautifulSoup.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

try:
    import requests
    from bs4 import BeautifulSoup
    _DEPS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _DEPS_AVAILABLE = False
    requests = None  # type: ignore[assignment]
    BeautifulSoup = None  # type: ignore[assignment]

_DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36 EducationalScraper/1.0"
)


class WebScraper:
    """Scrape links, text, headings, and images from web pages.

    Parameters
    ----------
    base_url:
        The root URL used to resolve relative links.
    delay:
        Seconds to wait between consecutive HTTP requests (rate limiting).
    timeout:
        Per-request timeout in seconds.
    max_retries:
        Number of retry attempts on transient network errors.
    """

    def __init__(
        self,
        base_url: str,
        delay: float = 1.0,
        timeout: int = 10,
        max_retries: int = 3,
    ) -> None:
        if not _DEPS_AVAILABLE:
            raise RuntimeError(
                "requests and beautifulsoup4 are required.\n"
                "Run: pip install requests beautifulsoup4 lxml"
            )

        self.base_url = base_url.rstrip("/")
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self._last_request_time: float = 0.0

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": _DEFAULT_UA})

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _rate_limit(self) -> None:
        """Block until the minimum inter-request delay has elapsed."""
        elapsed = time.time() - self._last_request_time
        wait = self.delay - elapsed
        if wait > 0:
            time.sleep(wait)

    def fetch_page(self, url: str) -> "requests.Response | None":
        """Fetch *url* with retries, rate-limiting, and error handling.

        Returns
        -------
        requests.Response or None
            *None* is returned (and a warning logged) on any unrecoverable error.
        """
        self._rate_limit()
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self._session.get(url, timeout=self.timeout)
                self._last_request_time = time.time()
                response.raise_for_status()
                logger.info("Fetched %s (status %s)", url, response.status_code)
                return response
            except requests.exceptions.ConnectionError:
                logger.warning(
                    "Connection error for %s (attempt %d/%d)",
                    url, attempt, self.max_retries,
                )
            except requests.exceptions.Timeout:
                logger.warning(
                    "Timeout for %s (attempt %d/%d)", url, attempt, self.max_retries
                )
            except requests.exceptions.HTTPError as exc:
                logger.error("HTTP error for %s: %s", url, exc)
                return None  # Non-transient — don't retry
            except requests.exceptions.RequestException as exc:
                logger.error("Request failed for %s: %s", url, exc)
                return None

            if attempt < self.max_retries:
                time.sleep(self.delay * attempt)  # exponential back-off

        logger.error("Giving up on %s after %d attempts", url, self.max_retries)
        return None

    def _parse(self, url: str) -> "BeautifulSoup | None":
        """Fetch and parse *url*; return a BeautifulSoup tree or None."""
        response = self.fetch_page(url)
        if response is None:
            return None
        return BeautifulSoup(response.text, "lxml")

    def _absolute(self, href: str | None) -> str:
        """Resolve *href* relative to base_url."""
        if not href:
            return ""
        return urljoin(self.base_url, href)

    # ------------------------------------------------------------------
    # Public scraping methods
    # ------------------------------------------------------------------

    def scrape_links(self, url: str) -> dict[str, Any]:
        """Extract all hyperlinks from *url*.

        Returns
        -------
        dict
            ``{"url": url, "count": n, "links": [list of absolute URLs]}``
        """
        soup = self._parse(url)
        if soup is None:
            return {"url": url, "count": 0, "links": [], "error": "Failed to fetch page"}

        links = []
        for tag in soup.find_all("a", href=True):
            absolute = self._absolute(tag["href"])
            if absolute:
                links.append(absolute)

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique.append(link)

        logger.info("scrape_links: found %d unique links at %s", len(unique), url)
        return {"url": url, "count": len(unique), "links": unique}

    def scrape_text(self, url: str) -> dict[str, Any]:
        """Extract paragraph text from *url*.

        Returns
        -------
        dict
            ``{"url": url, "count": n, "paragraphs": [list of strings]}``
        """
        soup = self._parse(url)
        if soup is None:
            return {"url": url, "count": 0, "paragraphs": [], "error": "Failed to fetch page"}

        paragraphs = [
            p.get_text(strip=True)
            for p in soup.find_all("p")
            if p.get_text(strip=True)
        ]
        logger.info("scrape_text: found %d paragraphs at %s", len(paragraphs), url)
        return {"url": url, "count": len(paragraphs), "paragraphs": paragraphs}

    def scrape_headings(self, url: str) -> dict[str, Any]:
        """Extract h1, h2, h3 headings from *url*.

        Returns
        -------
        dict
            ``{"url": url, "count": n, "headings": [{"level": "h1", "text": "…"}]}``
        """
        soup = self._parse(url)
        if soup is None:
            return {"url": url, "count": 0, "headings": [], "error": "Failed to fetch page"}

        headings = [
            {"level": tag.name, "text": tag.get_text(strip=True)}
            for tag in soup.find_all(["h1", "h2", "h3"])
            if tag.get_text(strip=True)
        ]
        logger.info("scrape_headings: found %d headings at %s", len(headings), url)
        return {"url": url, "count": len(headings), "headings": headings}

    def scrape_images(self, url: str) -> dict[str, Any]:
        """Extract image source URLs from *url*.

        Returns
        -------
        dict
            ``{"url": url, "count": n, "images": [list of absolute src URLs]}``
        """
        soup = self._parse(url)
        if soup is None:
            return {"url": url, "count": 0, "images": [], "error": "Failed to fetch page"}

        images = []
        for tag in soup.find_all("img", src=True):
            absolute = self._absolute(tag["src"])
            if absolute:
                images.append(absolute)

        logger.info("scrape_images: found %d images at %s", len(images), url)
        return {"url": url, "count": len(images), "images": images}

    def save_results(self, data: Any, filename: str) -> Path:
        """Persist *data* as pretty-printed JSON to *filename*.

        Parameters
        ----------
        data:
            Any JSON-serializable object.
        filename:
            Path (absolute or relative) for the output file.

        Returns
        -------
        Path
            Resolved path of the written file.
        """
        out = Path(filename)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        logger.info("Results saved to %s", out.resolve())
        return out.resolve()
