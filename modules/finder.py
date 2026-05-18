"""Finder stage — Google Maps business discovery via Playwright."""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime
from typing import Any
from urllib.parse import quote, unquote, urlparse

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright

from config import DEFAULT_MAX_RESULTS, HEADLESS, REQUEST_DELAY

logger = logging.getLogger(__name__)

MAPS_SEARCH_URL = "https://www.google.com/maps/search/{query}"
SOURCE = "google_maps"

BLOCKED_URL_FRAGMENTS = ("/sorry", "google.com/sorry")
BLOCKED_BODY_PHRASES = (
    "unusual traffic",
    "not a robot",
    "captcha",
    "before you continue",
    "detected unusual",
)
NO_RESULTS_PHRASES = (
    "no results found",
    "can't find",
    "couldn't find",
    "ni rezultatov",
    "ni mogoče najti",
    "keine ergebnisse",
)
NETWORK_ERROR_MARKERS = ("net::", "ns_error_", "connection refused", "err_connection", "timed out")


class FinderNetworkError(Exception):
    """Raised when Google Maps cannot be reached (network down, DNS, etc.)."""


class FinderBlockedError(Exception):
    """Raised when Google Maps blocks scraping; carries partial results if any."""

    def __init__(self, message: str, partial_results: list[dict[str, Any]] | None = None) -> None:
        super().__init__(message)
        self.partial_results = partial_results or []


def run(profile: dict[str, Any], log: logging.Logger) -> list[dict[str, Any]]:
    """
    Find businesses for the given profile on Google Maps.

    Returns lead dicts aligned with docs/05_output_spec.md (except website_live, set by enricher).
    On block mid-run, logs CRITICAL and returns partial results. On network failure, logs CRITICAL and raises.
    """
    keywords = profile.get("keywords") or []
    locations = profile.get("locations") or []
    if not keywords or not locations:
        log.warning("Finder: profile missing keywords or locations - nothing to search")
        return []

    max_results = int(profile.get("max_results") or DEFAULT_MAX_RESULTS)
    profile_name = profile.get("name", "unknown")

    log.info(
        "Finder: starting Google Maps search (keywords=%s, locations=%s, max=%d)",
        keywords,
        locations,
        max_results,
    )

    try:
        with GoogleMapsFinder(profile_name=profile_name, profile=profile, log=log) as finder:
            leads = finder.collect(max_results=max_results)
    except FinderNetworkError as exc:
        log.critical("Finder: network unavailable - %s", exc)
        raise
    except FinderBlockedError as exc:
        log.critical("Finder: Google Maps blocked request - %s", exc)
        partial = exc.partial_results
        if partial:
            log.info("Finder: returning %d partial result(s) collected before block", len(partial))
            return _apply_profile_filters(_dedupe_leads(partial), profile, log)
        return []

    leads = _apply_profile_filters(_dedupe_leads(leads), profile, log)

    if not leads:
        log.warning("Finder: Google Maps returned no results for this profile")
    else:
        log.info("Finder: collected %d business(es) after filters", len(leads))

    return leads


class GoogleMapsFinder:
    """Playwright-backed Google Maps scraper."""

    def __init__(self, profile_name: str, profile: dict[str, Any], log: logging.Logger) -> None:
        self.profile_name = profile_name
        self.profile = profile
        self.log = log
        self._playwright = None
        self._browser = None
        self._page: Page | None = None
        self._seen_urls: set[str] = set()

    def __enter__(self) -> GoogleMapsFinder:
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=HEADLESS)
        locale = "sl-SI" if self.profile.get("language") == "sl" else "en-US"
        context = self._browser.new_context(
            locale=locale,
            viewport={"width": 1280, "height": 900},
        )
        self._page = context.new_page()
        self._page.set_default_timeout(45_000)
        return self

    def __exit__(self, *args: object) -> None:
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("GoogleMapsFinder is not started")
        return self._page

    def collect(self, max_results: int) -> list[dict[str, Any]]:
        keywords: list[str] = self.profile.get("keywords") or []
        locations: list[str] = self.profile.get("locations") or []
        leads: list[dict[str, Any]] = []
        found_at = datetime.now().isoformat(timespec="seconds")

        for keyword in keywords:
            for location in locations:
                if len(leads) >= max_results:
                    break
                query = f"{keyword} {location}".strip()
                remaining = max_results - len(leads)
                self.log.info("Finder: searching %r (%d remaining)", query, remaining)
                try:
                    batch = self._search_query(query, location=location, found_at=found_at, limit=remaining)
                except FinderBlockedError:
                    raise FinderBlockedError(
                        "blocked during search",
                        partial_results=leads,
                    ) from None
                leads.extend(batch)
                _delay(REQUEST_DELAY)
            if len(leads) >= max_results:
                break

        return leads[:max_results]

    def _search_query(
        self,
        query: str,
        *,
        location: str,
        found_at: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        url = MAPS_SEARCH_URL.format(query=quote(query))
        self._safe_goto(url)
        _dismiss_consent(self.page)
        _delay(REQUEST_DELAY)

        if _is_blocked(self.page):
            raise FinderBlockedError("blocked on search results page")

        if _has_no_results(self.page):
            self.log.warning("Finder: no results for query %r", query)
            return []

        place_urls = self._collect_place_urls(limit)
        if not place_urls:
            self.log.warning("Finder: no place listings found for query %r", query)
            return []

        self.log.info("Finder: found %d listing(s) for %r", len(place_urls), query)
        leads: list[dict[str, Any]] = []

        for place_url in place_urls:
            if _is_blocked(self.page):
                raise FinderBlockedError("blocked while scraping listings")

            if place_url in self._seen_urls:
                continue
            self._seen_urls.add(place_url)

            try:
                lead = self._scrape_place(place_url, location=location, found_at=found_at)
            except FinderBlockedError:
                raise
            except PlaywrightError as exc:
                if _is_network_error(exc):
                    raise FinderNetworkError(str(exc)) from exc
                self.log.error("Finder: failed to scrape %s - %s", place_url, exc)
                continue

            if lead:
                leads.append(lead)
                self.log.debug("Finder: scraped %s", lead.get("name"))

            _delay(REQUEST_DELAY)

            if len(leads) >= limit:
                break

        return leads

    def _safe_goto(self, url: str) -> None:
        try:
            self.page.goto(url, wait_until="domcontentloaded")
        except PlaywrightError as exc:
            if _is_network_error(exc):
                raise FinderNetworkError(str(exc)) from exc
            raise

    def _collect_place_urls(self, limit: int) -> list[str]:
        page = self.page
        urls: list[str] = []
        seen: set[str] = set()
        stagnant_rounds = 0

        for _ in range(25):
            if len(urls) >= limit:
                break

            for href in _extract_place_hrefs(page):
                normalized = _normalize_maps_url(href)
                if normalized and normalized not in seen:
                    seen.add(normalized)
                    urls.append(normalized)

            if len(urls) >= limit:
                break

            before = len(urls)
            feed = page.locator('motion.div[role="feed"], div[role="feed"]')
            if feed.count() == 0:
                break
            try:
                feed.first.evaluate("el => { el.scrollTop = el.scrollHeight; }")
            except PlaywrightError:
                break
            _delay(min(REQUEST_DELAY, 1.5))

            if len(urls) == before:
                stagnant_rounds += 1
                if stagnant_rounds >= 3:
                    break
            else:
                stagnant_rounds = 0

        return urls[:limit]

    def _scrape_place(self, place_url: str, *, location: str, found_at: str) -> dict[str, Any] | None:
        self._safe_goto(place_url)
        _delay(REQUEST_DELAY * 0.5)

        if _is_blocked(self.page):
            raise FinderBlockedError("blocked on place detail page")

        page = self.page
        name = _first_text(
            page,
            "h1.DUwDvf",
            'h1[class*="fontHeadline"]',
            "h1",
        )
        if not name:
            self.log.warning("Finder: could not read business name from %s", place_url)
            return None

        category = _first_text(
            page,
            "button.DkEaL",
            'button[jsaction*="category"]',
        )
        address = _detail_field(page, "address", ("Address", "Naslov", "Adresse"))
        phone = _detail_field(page, "phone", ("Phone", "Telefon", "Tel", "Call"))
        website = _website_from_page(page)
        rating, review_count = _rating_from_page(page)
        if review_count is None:
            review_count = _review_count_from_page(page)

        return {
            "name": name,
            "category": category,
            "address": address,
            "city": _infer_city(location, address),
            "country": _infer_country(self.profile.get("locations") or [], address),
            "phone": phone,
            "website": website,
            "google_maps_url": place_url,
            "rating": rating,
            "review_count": review_count,
            "source": SOURCE,
            "profile_used": self.profile_name,
            "found_at": found_at,
            "notes": "",
        }


def _delay(seconds: float) -> None:
    if seconds > 0:
        time.sleep(seconds)


def _is_network_error(exc: BaseException) -> bool:
    message = str(exc).lower()
    return any(marker in message for marker in NETWORK_ERROR_MARKERS)


def _is_blocked(page: Page) -> bool:
    url = (page.url or "").lower()
    if any(fragment in url for fragment in BLOCKED_URL_FRAGMENTS):
        return True
    try:
        body = page.inner_text("body", timeout=5_000).lower()
    except PlaywrightError:
        body = ""
    return any(phrase in body for phrase in BLOCKED_BODY_PHRASES)


def _has_no_results(page: Page) -> bool:
    try:
        body = page.inner_text("body", timeout=5_000).lower()
    except PlaywrightError:
        return False
    return any(phrase in body for phrase in NO_RESULTS_PHRASES)


def _dismiss_consent(page: Page) -> None:
    selectors = (
        'button:has-text("Accept all")',
        'button:has-text("Sprejmi vse")',
        'button:has-text("Vse sprejmem")',
        'button:has-text("I agree")',
        "#L2AGLb",
    )
    for selector in selectors:
        button = page.locator(selector)
        if button.count() > 0:
            try:
                button.first.click(timeout=3_000)
                _delay(0.5)
                return
            except PlaywrightError:
                continue


def _extract_place_hrefs(page: Page) -> list[str]:
    hrefs: list[str] = []
    for link in page.locator('a[href*="/maps/place/"]').all():
        href = link.get_attribute("href")
        if href:
            hrefs.append(href)
    return hrefs


def _normalize_maps_url(href: str) -> str:
    href = href.strip()
    if href.startswith("/"):
        href = f"https://www.google.com{href}"
    parsed = urlparse(href)
    if "google.com" not in parsed.netloc:
        return ""
    base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        return f"{base}?{parsed.query}"
    return base


def _first_text(page: Page, *selectors: str) -> str:
    for selector in selectors:
        locator = page.locator(selector)
        if locator.count() == 0:
            continue
        try:
            text = locator.first.inner_text(timeout=3_000).strip()
            if text:
                return text
        except PlaywrightError:
            continue
    return ""


def _detail_field(page: Page, item_id: str, label_prefixes: tuple[str, ...]) -> str:
    locator = page.locator(f'button[data-item-id*="{item_id}"], [data-item-id*="{item_id}"]')
    if locator.count() == 0:
        return ""

    try:
        aria = (locator.first.get_attribute("aria-label") or "").strip()
        if aria:
            for prefix in label_prefixes:
                if aria.lower().startswith(prefix.lower()):
                    return aria[len(prefix) :].strip(" :")
            return aria
        text = locator.first.inner_text(timeout=3_000).strip()
        return text
    except PlaywrightError:
        return ""


def _website_from_page(page: Page) -> str:
    selectors = (
        'a[data-item-id="authority"]',
        'a[aria-label*="Website"]',
        'a[aria-label*="Spletna"]',
        'a[aria-label*="web"]',
    )
    for selector in selectors:
        locator = page.locator(selector)
        if locator.count() == 0:
            continue
        try:
            href = locator.first.get_attribute("href")
            if href:
                return _normalize_website_url(href)
        except PlaywrightError:
            continue
    return ""


def _normalize_website_url(url: str) -> str:
    url = unquote(url.strip())
    if "google.com/url" in url:
        parsed = urlparse(url)
        from urllib.parse import parse_qs

        q = parse_qs(parsed.query).get("q", [None])[0]
        if q:
            url = unquote(q)
    if url.startswith("//"):
        url = f"https:{url}"
    if url and not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url


def _rating_from_page(page: Page) -> tuple[str | None, int | None]:
    selectors = (
        'div.F7nice [aria-label*="star"]',
        'motion.div[role="img"][aria-label*="star"]',
        '[aria-label*="zvezd"]',
        '[aria-label*="stars"]',
        '[aria-label*="ocen"]',
    )
    for selector in selectors:
        locator = page.locator(selector)
        for index in range(min(locator.count(), 3)):
            try:
                label = locator.nth(index).get_attribute("aria-label")
                rating, reviews = _parse_rating_label(label or "")
                if rating is not None or reviews is not None:
                    return (
                        str(rating) if rating is not None else None,
                        reviews,
                    )
            except PlaywrightError:
                continue

    # Fallback: visible rating text near header
    text = _first_text(page, "div.F7nice span[aria-hidden='true']", "span.ceNzKf")
    if text:
        rating, reviews = _parse_rating_label(text)
        return (str(rating) if rating is not None else None, reviews)
    return None, None


def _review_count_from_page(page: Page) -> int | None:
    selectors = (
        'button[jsaction*="reviews"]',
        'button[aria-label*="reviews"]',
        'button[aria-label*="ocen"]',
        'span[aria-label*="reviews"]',
        'span[aria-label*="ocen"]',
    )
    for selector in selectors:
        locator = page.locator(selector)
        if locator.count() == 0:
            continue
        try:
            label = locator.first.get_attribute("aria-label") or locator.first.inner_text(timeout=2_000)
            if label:
                _, reviews = _parse_rating_label(label)
                if reviews is not None:
                    return reviews
                paren = re.search(r"\((\d[\d.,]*)\)", label.replace(",", ""))
                if paren:
                    return _parse_int(paren.group(1))
        except PlaywrightError:
            continue
    return None


def _parse_rating_label(label: str) -> tuple[float | None, int | None]:
    if not label:
        return None, None
    normalized = label.replace(",", ".")
    rating: float | None = None
    review_count: int | None = None

    paren = re.search(r"\((\d[\d.,]*)\)", normalized)
    if paren:
        review_count = _parse_int(paren.group(1))

    numbers = re.findall(r"\d+\.?\d*", normalized)
    if numbers:
        try:
            rating = float(numbers[0])
        except ValueError:
            rating = None
        if review_count is None and len(numbers) > 1:
            review_count = _parse_int(numbers[1])

    return rating, review_count


def _parse_int(value: str) -> int | None:
    digits = re.sub(r"[^\d]", "", value)
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def _infer_country(locations: list[str], address: str = "") -> str:
    joined = " ".join(locations).lower()
    addr_lower = (address or "").lower()
    if any(token in joined for token in ("sloven", "slovenija")):
        return "Slovenia"
    if any(token in addr_lower for token in ("slovenia", "slovenija")):
        return "Slovenia"
    # Slovenian addresses use 4-digit postal codes (e.g. "2000 Maribor")
    if re.search(r"\b\d{4}\s+\S", address or ""):
        return "Slovenia"
    for loc in locations:
        low = loc.lower().strip()
        if low in ("slovenia", "slovenija"):
            return "Slovenia"
        if low in ("austria", "croatia", "italy", "germany", "hungary"):
            return loc.strip().title()
    return ""


def _infer_city(location: str, address: str) -> str:
    loc = (location or "").strip()
    if loc and loc.lower() not in ("slovenija", "slovenia"):
        return loc.split(",")[0].strip()
    if address:
        parts = [part.strip() for part in address.split(",") if part.strip()]
        if parts:
            last = parts[-1]
            last = re.sub(r"^\d{4}\s*", "", last)
            return last
    return loc


def _dedupe_leads(leads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    unique: list[dict[str, Any]] = []
    for lead in leads:
        key = (
            (lead.get("name") or "").strip().lower(),
            (lead.get("address") or "").strip().lower(),
        )
        if key in seen and key != ("", ""):
            continue
        seen.add(key)
        unique.append(lead)
    return unique


def _apply_profile_filters(
    leads: list[dict[str, Any]],
    profile: dict[str, Any],
    log: logging.Logger,
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    excluded = 0

    require_website = bool(profile.get("require_website"))
    require_phone = bool(profile.get("require_phone"))
    min_reviews = profile.get("min_reviews")
    exclude_keywords = [kw.lower() for kw in (profile.get("exclude_keywords") or [])]

    for lead in leads:
        name_lower = (lead.get("name") or "").lower()

        if require_website and not (lead.get("website") or "").strip():
            excluded += 1
            continue
        if require_phone and not (lead.get("phone") or "").strip():
            excluded += 1
            continue
        if min_reviews is not None:
            count = lead.get("review_count")
            if count is None or count < int(min_reviews):
                excluded += 1
                continue
        if any(kw in name_lower for kw in exclude_keywords):
            excluded += 1
            continue

        filtered.append(lead)

    if excluded:
        log.info("Finder: excluded %d lead(s) by profile filters", excluded)
    return filtered
