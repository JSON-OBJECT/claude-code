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
| `/deep-thinking:deep-research {topic}` | Comprehensive multi-source research with 15+ searches, Reddit/news cross-validation, and Ki-Sho-Ten-Ketsu structured report |
| `/deep-thinking:pulse {field}` | Trend radar scanning 5+ subreddits and 75+ posts to identify hot issues before deep research |
| `/deep-thinking:forge-prompt {description}` | Create bulletproof instructions/skills with Iron Laws, anti-rationalization tables, and mandatory checklists |
| `/deep-thinking:meeting-notes {transcript}` | Transform meeting transcripts into narrative-driven documentation with counterparty research and verified terminology |

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
```

## Requirements

- Claude Code 1.0.33+

### MCP Server Dependencies

| Command | Required | Optional |
|---------|----------|----------|
| `/deep-thinking:deep-research` | Time, Brave Search, Reddit | - |
| `/deep-thinking:pulse` | Time, Brave Search, Reddit | - |
| `/deep-thinking:forge-prompt` | None | - |
| `/deep-thinking:meeting-notes` | Time, Brave Search | Context7, Fetch |

## License

MIT
