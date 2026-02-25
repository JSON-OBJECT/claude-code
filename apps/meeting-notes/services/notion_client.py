"""Notion API client for page search, creation, and block upload."""

import re

import httpx

from .markdown_to_blocks import md_to_blocks

NOTION_VERSION = "2022-06-28"
NOTION_BASE = "https://api.notion.com/v1"


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


async def search_pages(token: str, query: str = "") -> list[dict]:
    """Search Notion pages. Returns list of {id, title, url, icon}."""
    async with httpx.AsyncClient(timeout=30) as client:
        payload: dict = {
            "filter": {"value": "page", "property": "object"},
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
            "page_size": 20,
        }
        if query:
            payload["query"] = query
        resp = await client.post(
            f"{NOTION_BASE}/search",
            headers=_headers(token),
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

    pages = []
    for item in data.get("results", []):
        title_parts = item.get("properties", {}).get("title", {}).get("title", [])
        title = "".join(t.get("plain_text", "") for t in title_parts) if title_parts else "Untitled"
        icon = item.get("icon", {})
        icon_str = icon.get("emoji", "") if icon and icon.get("type") == "emoji" else ""
        pages.append({
            "id": item["id"],
            "title": title,
            "url": item.get("url", ""),
            "icon": icon_str,
        })
    return pages


async def create_page(
    token: str,
    parent_id: str,
    title: str,
    markdown: str,
    icon_emoji: str = "📝",
) -> dict:
    """Create a Notion page with markdown content. Returns {id, url}."""
    all_blocks = md_to_blocks(markdown)

    first_batch = all_blocks[:100]
    page_data = {
        "parent": {"page_id": parent_id},
        "icon": {"type": "emoji", "emoji": icon_emoji},
        "properties": {
            "title": [{"text": {"content": title}}]
        },
        "children": first_batch,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{NOTION_BASE}/pages",
            headers=_headers(token),
            json=page_data,
        )
        resp.raise_for_status()
        result = resp.json()
        page_id = result["id"]
        page_url = result["url"]

        # Upload remaining blocks in batches of 100
        remaining = all_blocks[100:]
        while remaining:
            batch = remaining[:100]
            remaining = remaining[100:]
            resp = await client.patch(
                f"{NOTION_BASE}/blocks/{page_id}/children",
                headers=_headers(token),
                json={"children": batch},
            )
            resp.raise_for_status()

    return {"id": page_id, "url": page_url}


def extract_page_id(url_or_id: str) -> str:
    """Extract a Notion page ID from a URL or raw ID string."""
    # Already a UUID-like ID
    clean = url_or_id.strip().replace("-", "")
    if re.match(r"^[a-f0-9]{32}$", clean):
        return url_or_id.strip()

    # Notion URL: https://www.notion.so/workspace/Page-Title-<32hex>
    # or https://www.notion.so/<32hex>
    m = re.search(r"([a-f0-9]{32})(?:\?|$)", url_or_id.replace("-", ""))
    if m:
        raw = m.group(1)
        return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"

    raise ValueError(f"Cannot extract Notion page ID from: {url_or_id}")
