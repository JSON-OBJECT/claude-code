"""Convert Markdown text to Notion API block objects."""

import re


def parse_rich_text(text: str) -> list[dict]:
    """Parse markdown inline formatting (bold, italic, code, links) into Notion rich_text array."""
    segments: list[dict] = []
    # Pattern: **bold**, *italic*, `code`, [text](url)
    pattern = re.compile(
        r"(\*\*(.+?)\*\*)"  # bold
        r"|(\*(.+?)\*)"  # italic
        r"|(`(.+?)`)"  # inline code
        r"|(\[([^\]]+)\]\(([^)]+)\))"  # link
    )
    last_end = 0
    for m in pattern.finditer(text):
        # plain text before this match
        if m.start() > last_end:
            plain = text[last_end : m.start()]
            if plain:
                segments.append(_text_segment(plain))

        if m.group(2):  # bold
            segments.append(_text_segment(m.group(2), bold=True))
        elif m.group(4):  # italic
            segments.append(_text_segment(m.group(4), italic=True))
        elif m.group(6):  # code
            segments.append(_text_segment(m.group(6), code=True))
        elif m.group(7):  # link
            link_text = m.group(8)
            link_url = m.group(9)
            segments.append(_text_segment(link_text, url=link_url))
        last_end = m.end()

    # trailing plain text
    if last_end < len(text):
        trailing = text[last_end:]
        if trailing:
            segments.append(_text_segment(trailing))

    if not segments:
        segments.append(_text_segment(text))
    return segments


def _text_segment(
    content: str,
    bold: bool = False,
    italic: bool = False,
    code: bool = False,
    url: str | None = None,
) -> dict:
    """Create a single Notion rich_text segment."""
    seg: dict = {
        "type": "text",
        "text": {"content": content[:2000]},
    }
    if url:
        seg["text"]["link"] = {"url": url}
    annotations: dict = {}
    if bold:
        annotations["bold"] = True
    if italic:
        annotations["italic"] = True
    if code:
        annotations["code"] = True
    if annotations:
        seg["annotations"] = annotations
    return seg


def md_to_blocks(md_text: str) -> list[dict]:
    """Convert markdown text to a list of Notion block objects."""
    blocks: list[dict] = []
    lines = md_text.split("\n")
    i = 0
    table_rows: list[list[str]] = []
    in_table = False

    while i < len(lines):
        line = lines[i]

        # Flush table if we leave table context
        if in_table and not line.startswith("|"):
            if table_rows:
                blocks.append(_build_table_block(table_rows))
                table_rows = []
            in_table = False

        # Table row
        if line.startswith("|"):
            stripped = line.strip()
            # Skip separator rows (|---|---|)
            if stripped.replace("|", "").replace("-", "").replace(" ", "").replace(":", "") == "":
                i += 1
                continue
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            table_rows.append(cells)
            in_table = True
            i += 1
            continue

        # Empty line
        if line.strip() == "":
            i += 1
            continue

        # Divider
        if line.strip() == "---":
            blocks.append({"object": "block", "type": "divider", "divider": {}})
            i += 1
            continue

        # Headings
        if line.startswith("### "):
            blocks.append({
                "object": "block", "type": "heading_3",
                "heading_3": {"rich_text": parse_rich_text(line[4:].strip())}
            })
            i += 1
            continue
        if line.startswith("## "):
            blocks.append({
                "object": "block", "type": "heading_2",
                "heading_2": {"rich_text": parse_rich_text(line[3:].strip())}
            })
            i += 1
            continue
        if line.startswith("# "):
            blocks.append({
                "object": "block", "type": "heading_1",
                "heading_1": {"rich_text": parse_rich_text(line[2:].strip())}
            })
            i += 1
            continue

        # Blockquote / Callout
        if line.startswith("> "):
            text = line[2:].strip()
            while i + 1 < len(lines) and lines[i + 1].startswith("> "):
                i += 1
                text += "\n" + lines[i][2:].strip()
            for chunk_start in range(0, len(text), 2000):
                blocks.append({
                    "object": "block", "type": "callout",
                    "callout": {
                        "rich_text": parse_rich_text(text[chunk_start:chunk_start + 2000]),
                        "icon": {"type": "emoji", "emoji": "📘"}
                    }
                })
            i += 1
            continue

        # Todo items
        if line.startswith("- [ ] "):
            blocks.append({
                "object": "block", "type": "to_do",
                "to_do": {"rich_text": parse_rich_text(line[6:].strip()), "checked": False}
            })
            i += 1
            continue
        if line.startswith("- [x] "):
            blocks.append({
                "object": "block", "type": "to_do",
                "to_do": {"rich_text": parse_rich_text(line[6:].strip()), "checked": True}
            })
            i += 1
            continue

        # Code block
        if line.startswith("```"):
            code_text = ""
            lang = line[3:].strip() or "plain text"
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_text += lines[i] + "\n"
                i += 1
            valid_langs = {
                "javascript", "python", "java", "c", "cpp", "go", "rust",
                "ruby", "php", "sql", "html", "css", "json", "yaml",
                "markdown", "plain text", "typescript", "shell", "bash",
            }
            blocks.append({
                "object": "block", "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": code_text.rstrip()[:2000]}}],
                    "language": lang if lang in valid_langs else "plain text"
                }
            })
            i += 1
            continue

        # Numbered list
        if len(line) > 2 and line[0].isdigit() and (
            line[1] in ".)" or (len(line) > 3 and line[:2].isdigit() and line[2] in ".)")
        ):
            idx = line.index(" ") if " " in line else 0
            text = line[idx + 1:].strip() if idx else line
            blocks.append({
                "object": "block", "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": parse_rich_text(text)}
            })
            i += 1
            continue

        # Bulleted list
        if line.startswith("- "):
            blocks.append({
                "object": "block", "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": parse_rich_text(line[2:].strip())}
            })
            i += 1
            continue

        # Paragraph (merge consecutive non-special lines)
        text = line.strip()
        if text:
            while (
                i + 1 < len(lines)
                and lines[i + 1].strip()
                and not lines[i + 1].startswith("#")
                and not lines[i + 1].startswith(">")
                and not lines[i + 1].startswith("- ")
                and not lines[i + 1].startswith("|")
                and not lines[i + 1].startswith("```")
                and lines[i + 1].strip() != "---"
            ):
                i += 1
                text += "\n" + lines[i].strip()
            for chunk_start in range(0, len(text), 2000):
                blocks.append({
                    "object": "block", "type": "paragraph",
                    "paragraph": {"rich_text": parse_rich_text(text[chunk_start:chunk_start + 2000])}
                })
        i += 1

    # Flush remaining table
    if table_rows:
        blocks.append(_build_table_block(table_rows))

    return blocks


def _build_table_block(table_rows: list[list[str]]) -> dict:
    """Build a Notion table block from parsed rows."""
    col_count = len(table_rows[0])
    children = []
    for row in table_rows:
        cells = []
        for cell in row:
            cells.append([{"type": "text", "text": {"content": cell[:2000]}}])
        while len(cells) < col_count:
            cells.append([{"type": "text", "text": {"content": ""}}])
        children.append({
            "type": "table_row",
            "table_row": {"cells": cells[:col_count]}
        })
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": col_count,
            "has_column_header": True,
            "has_row_header": False,
            "children": children,
        },
    }
