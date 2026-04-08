# trello-mcp — MCP Server for Trello

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-stdio-green.svg)](https://modelcontextprotocol.io)

An MCP server that gives Claude Desktop and Claude Code full
access to the Trello API. Built on the
[trellio](https://github.com/scaratec/trellio) async client
library and the official Python MCP SDK.

## Features

- **38 MCP tools** — 1:1 mapping to trellio methods, plus one
  composite `get_board_overview` tool
- **2 resource templates** — `trello://board/{id}` and
  `trello://card/{id}` for rich context loading
- **3 prompts** — `summarize_board`, `create_sprint`,
  `daily_standup` as workflow shortcuts
- **Structured error handling** — Trello API errors are
  translated into clear, actionable MCP error messages
- **stdio transport** — runs as a local subprocess, no network
  surface

## Tools

| Category    | Tools | Methods |
|-------------|-------|---------|
| Discovery   | `list_boards`, `search` | 2 |
| Boards      | `get_board_overview`, `create_board`, `get_board`, `update_board`, `delete_board` | 5 |
| Lists       | `list_lists`, `create_list` | 2 |
| Cards       | `list_cards`, `create_card`, `get_card`, `update_card`, `delete_card` | 5 |
| Labels      | `list_board_labels`, `create_label`, `update_label`, `delete_label` | 4 |
| Checklists  | `list_card_checklists`, `create_checklist`, `delete_checklist`, `create_check_item`, `update_check_item`, `delete_check_item` | 6 |
| Comments    | `list_comments`, `add_comment`, `update_comment`, `delete_comment` | 4 |
| Members     | `get_me`, `list_board_members`, `get_member` | 3 |
| Attachments | `list_attachments`, `create_attachment`, `delete_attachment` | 3 |
| Webhooks    | `list_webhooks`, `create_webhook`, `get_webhook`, `update_webhook`, `delete_webhook` | 5 |

## Prerequisites

- Python 3.10+
- A [Trello API Key and Token](https://trello.com/power-ups/admin)

## Installation

```bash
git clone https://github.com/scaratec/trello-mcp.git
cd trello-mcp
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "trello": {
      "command": "/path/to/trello-mcp/.venv/bin/python",
      "args": ["-m", "trello_mcp"],
      "env": {
        "TRELLO_API_KEY": "your_api_key",
        "TRELLO_TOKEN": "your_token"
      }
    }
  }
}
```

### Claude Code

Add to `~/.claude/settings.json` or project `.claude/settings.json`:

```json
{
  "mcpServers": {
    "trello": {
      "command": "/path/to/trello-mcp/.venv/bin/python",
      "args": ["-m", "trello_mcp"],
      "env": {
        "TRELLO_API_KEY": "your_api_key",
        "TRELLO_TOKEN": "your_token"
      }
    }
  }
}
```

### Manual

```bash
TRELLO_API_KEY=your_key TRELLO_TOKEN=your_token \
  .venv/bin/python -m trello_mcp
```

## Architecture

```
MCP Client (Claude)
    │ stdio (JSON-RPC)
    ▼
trello-mcp (FastMCP)
    │ async/await
    ▼
trellio (httpx)
    │ HTTPS
    ▼
Trello API
```

**Key decisions** (documented in `docs/adr/`):

| ADR | Decision |
|-----|----------|
| 001 | Python MCP SDK for language alignment with trellio |
| 002 | stdio transport — no network attack surface |
| 003 | Environment variables only for credentials |
| 004 | 1:1 tool mapping — one tool per trellio method |
| 005 | trellio as Git dependency pinned to v1.0.0 |
| 006 | Tools + Resources + Prompts as MCP capabilities |
| 007 | `isError=true` + structured error content |

## Testing

The project uses BDD with
[behave](https://behave.readthedocs.io/), following the
[BDD Guidelines v1.8.0](https://github.com/scaratec/burn-your-code).

```bash
PYTHONPATH=src .venv/bin/python -m behave
```

```
14 features passed, 0 failed, 0 skipped
103 scenarios passed, 0 failed, 0 skipped
634 steps passed, 0 failed, 0 skipped
```

Test architecture:
- `AsyncMock(spec=TrellioClient)` — mock at the client
  boundary, not HTTP
- Persistence validation via mock call records (§4.3)
- Anti-hardcoding via Scenario Outlines with ≥ 2 variants
  (§2.3)
- Layer-by-layer failure path enumeration: 11 error scenarios
  (§4.5)
- Independent spec audit per §13

## Project Structure

```
trello-mcp/
├── src/trello_mcp/
│   ├── __init__.py        # Tool registration
│   ├── __main__.py        # Entry point
│   ├── server.py          # FastMCP instance + client mgmt
│   ├── errors.py          # Error translation (ADR 007)
│   ├── tools/             # 10 modules, 38 tools
│   ├── resources.py       # 2 resource templates
│   └── prompts.py         # 3 prompts
├── features/              # 14 BDD feature files
│   └── steps/             # Step definitions
├── docs/
│   ├── adr/               # 7 Architecture Decision Records
│   └── tool-design.md     # Scenario-driven tool analysis
└── pyproject.toml
```

## License

This project is licensed under the GNU General Public License
v3.0 — see the [LICENSE](LICENSE) file for details.
