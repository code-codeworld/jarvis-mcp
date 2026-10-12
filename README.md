# J.A.R.V.I.S. Personal MCP Server
## Jordan Advanced Resource & Venture Intelligence System

Your personal AI command center — talk to it and it knows your world.

## Tools Available

| Tool | What you ask |
|------|-------------|
| `get_full_briefing` | "Give me my morning briefing" |
| `get_444_status` | "What's going on with 444?" |
| `get_job_search_status` | "Where am I with my job search?" |
| `get_wgu_progress` | "How is school going?" |
| `get_personal_intel` | "What personal things need attention?" |
| `get_garden_status` | "What should I plant right now?" |
| `get_wiz_news` | "What did Wiz publish this week?" |
| `search_jobs` | "Find me SSPM security jobs" |
| `read_memory` | "What do you remember about the shed buyout?" |
| `get_444_social_ideas` | "Give me Instagram post ideas for 444" |

## Setup with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "jarvis": {
      "command": "python3",
      "args": ["/Users/lukeskywalker/Projects/jarvis-mcp/server.py"],
      "env": {
        "BRAVE_API_KEY": "BSAi9dF8HAyfFvx7ZfuEDKTCUFh1bUY"
      }
    }
  }
}
```

Then restart Claude Desktop. The tools will appear automatically.

## Usage Examples

- "Good morning JARVIS, what's my briefing?"
- "Any new security jobs posted this week?"
- "What should I post on TikTok for 444 this week?"
- "What's the status on the court case?"
- "What do you remember about the land quest?"
- "What's happening with my WGU courses?"
