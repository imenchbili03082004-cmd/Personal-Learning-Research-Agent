from typing import Annotated

from langchain_core.tools import tool
from ollama import Client


ollama = Client(
    host="https://ollama.com"
)


@tool
def web_search(
    query: Annotated[str, "The search query"],
    max_results: Annotated[int, "Maximum number of results"] = 5,
):
    """
    Search the web and return relevant results.
    """

    max_results = max(1, min(max_results, 5))

    response = ollama.web_search(
        query=query,
        max_results=max_results
    )

    if not response.results:
        return "No search results found."

    results = []

    for result in response.results:
        results.append(
            {
                "title": result.title,
                "url": result.url,
                "content": result.content,
            }
        )

    return results


@tool
def web_fetch(
    url: Annotated[str, "The URL of the web page to fetch"]
):
    """
    Fetch the content of a web page.
    """

    response = ollama.web_fetch(
        url=url
    )

    return response


tools = [
    web_search,
    web_fetch,
]