# Deep Thinking Plugin

A Claude Code plugin for deep research, prompt engineering, trend analysis, and meeting documentation.

## Installation

```bash
# Add marketplace (one-time setup)
/plugin marketplace add JSON-OBJECT/claude-code

# Install plugin
/plugin install deep-thinking@jsonobject-marketplace
```

## Commands

| Command | Description |
|---------|-------------|
| `/deep-thinking:pulse {topic}` | Trend radar scanning 5+ subreddits and 75+ posts to identify hot issues before deep research |
| `/deep-thinking:deep-research {topic}` | Comprehensive multi-source research with 15+ searches, Reddit/news cross-validation, and Ki-Sho-Ten-Ketsu structured report |
| `/deep-thinking:forge-prompt {instruction}` | Create bulletproof instructions/skills with Iron Laws, anti-rationalization tables, and mandatory checklists |
| `/deep-thinking:meeting-notes {transcript}` | Transform meeting transcripts into narrative-driven documentation with counterparty research and verified terminology |
| `/deep-thinking:translate-kr {article}` | Transcreate English IT articles into native Korean with terminology verification and anti-translation-artifact rules |
| `/deep-thinking:blog-cover {title and concept}` | Generate anti-AI-looking blog cover image prompts for Gemini Nano Banana Pro with visual metaphors and title typography |

## Usage Examples

```bash
# Discover trending topics in a field
/deep-thinking:pulse AI agents

# Deep dive into a specific topic
/deep-thinking:deep-research Claude Code plugin marketplace best practices

# Create a new skill/instruction
/deep-thinking:forge-prompt code review checklist for security vulnerabilities

# Process meeting transcript
/deep-thinking:meeting-notes [paste transcript or provide file path]

# Translate English IT article to Korean
/deep-thinking:translate-kr [paste English article or provide file path]

# Generate blog cover image prompt
/deep-thinking:blog-cover "Why Microservices Fail" | "complexity debt accumulates faster than you think"
```

## Requirements

- Claude Code 1.0.33+

### MCP Server Dependencies

| Command | Required | Optional |
|---------|----------|----------|
| `/deep-thinking:pulse` | Time, Brave Search, Reddit | - |
| `/deep-thinking:deep-research` | Time, Brave Search, Reddit | - |
| `/deep-thinking:forge-prompt` | None | - |
| `/deep-thinking:meeting-notes` | Time, Brave Search | Context7, Fetch |
| `/deep-thinking:translate-kr` | Brave Search | - |
| `/deep-thinking:blog-cover` | None | - |

### Quick MCP Setup

```bash
# Time
claude mcp add time -s user -- uvx mcp-server-time

# Brave Search (get API key: https://brave.com/search/api)
claude mcp add-json -s user brave-search '{"command":"npx","args":["-y","brave-search-mcp"],"env":{"BRAVE_API_KEY":"YOUR_API_KEY"}}'

# Reddit
claude mcp add reddit -s user -- uvx --from git+https://github.com/adhikasp/mcp-reddit.git mcp-reddit

# Context7 (Library Documentation)
claude mcp add context7 -s user -- npx -y @upstash/context7-mcp

# Fetch (Web Crawling)
claude mcp add fetch -s user -- uvx mcp-server-fetch
```

## License

MIT
