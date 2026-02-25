"""Meeting Notes Web App — FastAPI entry point."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from services.anthropic_client import generate_meeting_notes
from services.notion_client import create_page, extract_page_id, search_pages

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
MODEL = os.getenv("MODEL", "claude-haiku-4-5-20251001")
SONNET_MODEL = "claude-sonnet-4-5-20250929"

TEMPLATE_DIR = Path(__file__).parent / "templates"
SYSTEM_PROMPT = (TEMPLATE_DIR / "system_prompt.md").read_text(encoding="utf-8")

# Load glossary if available (repo root: ../../glossary.md)
GLOSSARY_PATH = Path(__file__).parent.parent.parent / "glossary.md"
if GLOSSARY_PATH.exists():
    _glossary = GLOSSARY_PATH.read_text(encoding="utf-8")
    SYSTEM_PROMPT += f"\n\n## Domain Glossary (STT 오류 교정 + 용어 정의 참조)\n\n{_glossary}"

app = FastAPI(title="Meeting Notes Generator")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


# --- Notion Routes ---


@app.get("/api/notion/pages")
async def get_notion_pages(q: str = ""):
    if not NOTION_API_KEY:
        raise HTTPException(status_code=500, detail="NOTION_API_KEY not configured")
    pages = await search_pages(NOTION_API_KEY, q)
    return {"pages": pages}


class ProcessRequest(BaseModel):
    notion_url: str
    text: str
    mode: str = "concise"


@app.post("/api/process")
async def process_meeting(request: Request, body: ProcessRequest):
    """Process meeting transcript → AI notes → Notion upload. Streams SSE events."""
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
    if not NOTION_API_KEY:
        raise HTTPException(status_code=500, detail="NOTION_API_KEY not configured")

    if len(body.text.strip()) < 100:
        raise HTTPException(status_code=400, detail="텍스트가 너무 짧습니다 (최소 100자)")

    try:
        parent_id = extract_page_id(body.notion_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    async def event_stream():
        final_markdown = ""

        use_model = SONNET_MODEL if body.mode == "sonnet" else MODEL

        async for event in generate_meeting_notes(
            anthropic_api_key=ANTHROPIC_API_KEY,
            model=use_model,
            system_prompt=SYSTEM_PROMPT,
            user_message=body.text,
            mode=body.mode,
        ):
            evt = event.get("event", "")
            data = event.get("data", "")

            if evt == "result":
                final_markdown = data
                yield {"event": "composing", "data": "회의록 작성 완료, 노션 업로드 중..."}

                # Upload to Notion
                try:
                    yield {"event": "uploading", "data": "노션 페이지 생성 중..."}

                    # Extract title from markdown (first # heading)
                    title = "Meeting Notes"
                    for line in final_markdown.split("\n"):
                        if line.startswith("# "):
                            title = line[2:].strip()
                            # Remove date suffix like " — 2025-01-15" for cleaner title
                            break

                    result = await create_page(
                        token=NOTION_API_KEY,
                        parent_id=parent_id,
                        title=title,
                        markdown=final_markdown,
                    )
                    yield {
                        "event": "done",
                        "data": json.dumps({
                            "notion_url": result["url"],
                            "markdown": final_markdown,
                        }),
                    }
                except Exception as e:
                    yield {
                        "event": "error",
                        "data": json.dumps({
                            "message": f"노션 업로드 실패: {e}",
                            "markdown": final_markdown,
                        }),
                    }
            elif evt == "error":
                yield {"event": "error", "data": json.dumps({"message": data, "markdown": ""})}
            else:
                yield {"event": evt, "data": data}

    return EventSourceResponse(event_stream())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
