
from typing import Annotated
from urllib.parse import urlparse
import time

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from langchain_core.tools import tool

MAX_RESULTS = 3
MAX_SEARCH_CONTENT_CHARS = 2000
MAX_FETCH_CONTENT_CHARS = 8000

SEARCH_TIMEOUT = 30
SEARCH_RETRIES = 3

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ResearchAssistant/1.0)"
}


@tool
def web_search(
    query: Annotated[str, "The search query"],
    max_results: Annotated[int, "Maximum number of results"] = 3,
):
    """Search the web and return relevant results."""

    max_results = max(1, min(max_results, MAX_RESULTS))

    for attempt in range(SEARCH_RETRIES):
        try:
            with DDGS(timeout=SEARCH_TIMEOUT) as ddgs:
                results = list(
                    ddgs.text(
                        query,
                        max_results=max_results,
                    )
                )

            if not results:
                return "No search results found for this query."

            return [
                {
                    "title": item.get("title", ""),
                    "url": item.get("href", ""),
                    "content": item.get("body", "")[
                        :MAX_SEARCH_CONTENT_CHARS
                    ],
                }
                for item in results
            ]

        except Exception as exc:
            print(
                f"Search attempt {attempt + 1}/"
                f"{SEARCH_RETRIES} failed: {exc}"
            )

            if attempt < SEARCH_RETRIES - 1:
                time.sleep(2 * (attempt + 1))

    return (
        "Web search temporarily unavailable after "
        f"{SEARCH_RETRIES} attempts. "
        "Try again later or use another search provider."
    )


@tool
def web_fetch(
    url: Annotated[str, "The URL of the web page to fetch"]
):
    """Fetch a web page and extract its text."""

    parsed = urlparse(url)

    if parsed.scheme != "https" or not parsed.hostname:
        return "Only valid HTTPS URLs are allowed."

    if parsed.hostname.lower() in {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
    }:
        return "Local URLs are not allowed."

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15,
            allow_redirects=True,
        )
        response.raise_for_status()

        # Check the final URL after redirects.
        final_url = urlparse(response.url)

        if (
            final_url.scheme != "https"
            or not final_url.hostname
            or final_url.hostname.lower()
            in {"localhost", "127.0.0.1", "0.0.0.0"}
        ):
            return "Redirect to a disallowed URL."

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for tag in soup(
            ["script", "style", "nav", "footer", "header"]
        ):
            tag.decompose()

        content = soup.get_text(
            separator=" ",
            strip=True,
        )

        return content[:MAX_FETCH_CONTENT_CHARS]

    except requests.RequestException as exc:
        return f"Unable to fetch page: {exc}"
