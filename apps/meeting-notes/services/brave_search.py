"""Brave Search REST API wrapper."""

import httpx

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


async def search(api_key: str, query: str, count: int = 5) -> str:
    """Search using Brave Search API. Returns formatted top results as a string."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            BRAVE_SEARCH_URL,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": api_key,
            },
            params={"q": query, "count": count},
        )
        resp.raise_for_status()
        data = resp.json()

    results = data.get("web", {}).get("results", [])
    if not results:
        return f"No results found for: {query}"

    formatted = []
    for i, r in enumerate(results[:count], 1):
        title = r.get("title", "")
        url = r.get("url", "")
        desc = r.get("description", "")
        formatted.append(f"{i}. [{title}]({url})\n   {desc}")

    return "\n\n".join(formatted)
