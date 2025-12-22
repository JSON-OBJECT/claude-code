# Claude Code Quick Setup

Anthropic's AI-powered terminal coding assistant with MCP Server integration.

## Prerequisites

```bash
# Install Node
nvm install node && nvm alias default node

# Install uv (for Python-based MCP servers)
brew install uv
```

## Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code

# Environment variables for non-English input lag fix
echo 'export TERM=xterm-256color' >> ~/.bashrc
echo 'export LC_ALL=C.UTF-8' >> ~/.bashrc
```

## Authentication

### Anthropic Console (Pro plan required)

```bash
claude
> /login
```

### Amazon Bedrock

```bash
export AWS_ACCESS_KEY_ID={your-key}
export AWS_SECRET_ACCESS_KEY={your-secret}
export AWS_REGION_NAME=us-west-1
export CLAUDE_CODE_USE_BEDROCK=1
```

### Custom LLM Gateway

```bash
export ANTHROPIC_BASE_URL={your-gateway-url}
export ANTHROPIC_AUTH_TOKEN={your-auth-token}
```

## Basic Usage

```bash
claude           # New session
claude -c        # Continue last session
claude -r        # Resume specific session
```

```bash
> /clear                    # Reset context
> /model opus               # Switch to Opus 4.5
> /model sonnet             # Switch to Sonnet 4.5
> /model sonnet[1m]         # Sonnet 4.5 with 1M context
> @{file-path} {prompt}     # Include files
> {prompt} ultrathink       # Enable extended thinking
> /compact "{instructions}" # Manual context compaction
```

**Mode Switching:**
- `TAB` - Toggle extended thinking
- `SHIFT+TAB` (2x) - Enter Plan Mode (read-only analysis)
- `SHIFT+TAB` (1x) - Exit to Edit Mode

## MCP Servers Installation

### Time

```bash
claude mcp add time -s user -- uvx mcp-server-time
```

### Context7 (Library Documentation)

```bash
claude mcp add context7 -s user -- npx -y @upstash/context7-mcp
```

### Brave Search

Get API key from [brave.com/search/api](https://brave.com/search/api) (Free: 5,000 queries/month)

```bash
claude mcp add-json -s user brave-search '{"command":"npx","args":["-y","brave-search-mcp"],"env":{"BRAVE_API_KEY":"{your-key}"}}'
```

### Fetch (Advanced Web Crawling)

```bash
claude mcp add fetch -s user -- uvx mcp-server-fetch
```

### Reddit

```bash
claude mcp add reddit -s user -- uvx --from git+https://github.com/adhikasp/mcp-reddit.git mcp-reddit
```

### Playwright (Browser Automation)

```bash
npm install -g @executeautomation/playwright-mcp-server
claude mcp add playwright -s user -- npx -y @executeautomation/playwright-mcp-server
```

### Serena (LSP + Long-term Memory RAG)

```bash
# Run from project root
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project $(pwd)

# Initial onboarding
claude
> start Serena onboarding
```

### Slack

```bash
claude mcp add-json -s user slack '{"command":"npx","args":["-y","slack-mcp-server@latest"],"env":{"SLACK_MCP_XOXP_TOKEN":"{your-token}"}}'
```

### Notion

```bash
claude mcp add-json -s user notion '{"command":"npx","args":["-y","@notionhq/notion-mcp-server"],"env":{"NOTION_TOKEN":"{your-token}"}}'
```

## Memory: CLAUDE.md

Claude Code uses `CLAUDE.md` files as persistent memory:

| Path | Scope |
|------|-------|
| `~/.claude/CLAUDE.md` | Global (all projects) |
| `./CLAUDE.md` | Project-specific |

The `CLAUDE.md` in this repository root serves as the **global memory** template, defining behavioral rules, MCP server usage patterns, and response preferences.

## Custom Slash Commands

Located in `./commands/`:

| Command | Description |
|---------|-------------|
| `/pulse {field}` | Trend radar scanning 5+ subreddits and 75+ posts to identify hot issues before deep research |
| `/deep-research {topic}` | Comprehensive multi-source research with 15+ searches, Reddit/news cross-validation, and Ki-Sho-Ten-Ketsu structured report |
| `/meeting-notes {transcript}` | Transform meeting transcripts into narrative-driven documentation with counterparty research and verified terminology |
| `/forge-prompt {description}` | Create bulletproof instructions/skills with Iron Laws, anti-rationalization tables, and mandatory checklists |

## References

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices/)
- [Claude Code Common Workflows](https://code.claude.com/docs/en/common-workflows)
