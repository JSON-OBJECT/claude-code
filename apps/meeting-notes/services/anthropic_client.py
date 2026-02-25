"""Anthropic API client for meeting notes generation. Single-call, no tools."""

import logging
from collections.abc import AsyncGenerator
from datetime import datetime, timezone, timedelta

import anthropic

logger = logging.getLogger("uvicorn.error")


DETAILED_ADDENDUM = (
    "\n\n## DETAILED MODE OVERRIDE\n"
    "- ZERO DETAIL LOSS — every decision, metric, technical fact MUST appear.\n"
    "- Each topic: 4-8 sentences (Problem → Discussion → Solution → Result → Implications).\n"
    "- Add **Implications** subsection after Key Learnings.\n"
    "- Add **Parked Items** section for unresolved topics.\n"
    "- Add **References** section for mentioned links, documents, tools.\n"
)


async def generate_meeting_notes(
    anthropic_api_key: str,
    model: str,
    system_prompt: str,
    user_message: str,
    mode: str = "concise",
) -> AsyncGenerator[dict, None]:
    """
    Single Anthropic API call for meeting notes generation (no tool loop).

    Yields SSE-compatible event dicts:
      {"event": "started"}
      {"event": "composing"}
      {"event": "result", "data": "final markdown"}
      {"event": "error", "data": "error message"}
    """
    client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)

    # Inject current time into system prompt
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    current_time = now.strftime("%Y-%m-%d %H:%M KST (%A)")
    system = system_prompt.replace("{current_time}", current_time)

    # Adjust for output mode
    if mode == "sonnet":
        system += DETAILED_ADDENDUM
        max_tokens = 16384
    elif mode == "detailed":
        system += DETAILED_ADDENDUM
        max_tokens = 16384
    else:
        max_tokens = 8192

    yield {"event": "started"}
    yield {"event": "composing", "data": f"회의록 생성 중... ({mode} 모드)"}

    try:
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
    except Exception as e:
        yield {"event": "error", "data": str(e)}
        return

    # Log token usage for cost analysis (model-specific pricing)
    usage = response.usage
    input_tokens = usage.input_tokens
    output_tokens = usage.output_tokens
    if "sonnet" in response.model:
        in_price, out_price = 3.0, 15.0
    else:  # haiku
        in_price, out_price = 0.80, 4.0
    logger.warning(
        f"[COST] model={response.model} input={input_tokens} output={output_tokens} "
        f"input_cost=${input_tokens * in_price / 1_000_000:.4f} "
        f"output_cost=${output_tokens * out_price / 1_000_000:.4f} "
        f"total=${input_tokens * in_price / 1_000_000 + output_tokens * out_price / 1_000_000:.4f}"
    )

    text_parts = []
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)

    if text_parts:
        yield {"event": "result", "data": "\n".join(text_parts)}
    else:
        yield {"event": "error", "data": "No text in response"}
