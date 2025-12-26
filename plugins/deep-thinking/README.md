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
| `/dt:deep-research {topic}` | Comprehensive multi-source research with 15+ searches, Reddit/news cross-validation, and Ki-Sho-Ten-Ketsu structured report |
| `/dt:pulse {field}` | Trend radar scanning 5+ subreddits and 75+ posts to identify hot issues before deep research |
| `/dt:forge-prompt {description}` | Create bulletproof instructions/skills with Iron Laws, anti-rationalization tables, and mandatory checklists |
| `/dt:meeting-notes {transcript}` | Transform meeting transcripts into narrative-driven documentation with counterparty research and verified terminology |

## Usage Examples

```bash
# Discover trending topics in a field
/dt:pulse AI agents

# Deep dive into a specific topic
/dt:deep-research Claude Code plugin marketplace best practices

# Create a new skill/instruction
/dt:forge-prompt code review checklist for security vulnerabilities

# Process meeting transcript
/dt:meeting-notes [paste transcript or provide file path]
```

## Requirements

- Claude Code 1.0.33+
- **MCP Servers (required for full functionality):**
  - Brave Search MCP (for `/dt:deep-research`, `/dt:pulse`)
  - Reddit MCP (for `/dt:pulse`)
  - Time MCP (for temporal context)
  - Fetch MCP (for web content extraction)

## License

MIT
