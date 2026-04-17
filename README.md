# trellio-mcp — MCP Server for Trello

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-stdio-green.svg)](https://modelcontextprotocol.io)

<!-- mcp-name: io.github.scaratec/trellio-mcp -->

An MCP server that gives Claude Desktop, Claude Code, and
Gemini CLI full access to the Trello API. Built on the
[trellio](https://github.com/scaratec/trellio) async client
library and the official Python MCP SDK. Developed following
the [BDD Guidelines v1.8.0](https://github.com/scaratec/burn-your-code).

## Features

- **48 MCP tools** — 1:1 mapping to trellio methods, plus
  one composite `get_board_overview` tool
- **2 resource templates** — `trello://board/{id}` and
  `trello://card/{id}` for rich context loading
- **3 prompts** — `summarize_board`, `create_sprint`,
  `daily_standup` as workflow shortcuts
- **Built-in auth flow** — `python -m trello_mcp auth` opens
  the browser, user clicks "Allow", token stored securely
- **Structured error handling** — Trello API errors are
  translated into clear, actionable MCP error messages
- **stdio transport** — runs as a local subprocess, no
  network surface

## Tools

| Category    | Tools | Count |
|-------------|-------|-------|
| Discovery   | `list_boards`, `search` | 2 |
| Boards      | `get_board_overview`, `create_board`, `get_board`, `update_board`, `delete_board` | 5 |
| Lists       | `list_lists`, `create_list`, `update_list`, `archive_list` | 4 |
| Cards       | `list_cards`, `create_card`, `get_card`, `update_card`, `archive_card`, `unarchive_card`, `delete_card`, `add_label_to_card`, `remove_label_from_card` | 9 |
| Labels      | `list_board_labels`, `create_label`, `update_label`, `delete_label` | 4 |
| Checklists  | `list_card_checklists`, `create_checklist`, `delete_checklist`, `create_check_item`, `update_check_item`, `delete_check_item` | 6 |
| Comments    | `list_comments`, `add_comment`, `update_comment`, `delete_comment` | 4 |
| Members     | `get_me`, `list_board_members`, `get_member` | 3 |
| Attachments | `list_attachments`, `create_attachment`, `get_attachment`, `upload_attachment`, `download_attachment`, `delete_attachment` | 6 |
| Webhooks    | `list_webhooks`, `create_webhook`, `get_webhook`, `update_webhook`, `delete_webhook` | 5 |

Card tools support `pos` (top/bottom), `idLabels`
(comma-separated), `due` (ISO 8601), and `dueComplete`
(true/false) on create and update.

## Prerequisites

- Python 3.10+
- A [Trello API Key](https://trello.com/power-ups/admin)
  (add `http://localhost:8095` to Allowed Origins)

## Installation

### Smithery

[![smithery badge](https://smithery.ai/badge/gupta/trellio-mcp)](https://smithery.ai/server/gupta/trellio-mcp)

```bash
npx @smithery/cli install gupta/trellio-mcp --client claude
```

### Using pipx (recommended)

To install globally so the `trellio-mcp` command is available in your PATH:

```bash
pipx install trellio-mcp
```

Alternatively, you can run it on-the-fly without installing:

```bash
pipx run trellio-mcp
```
*(Note: If you use `pipx run`, your MCP client configuration must also use `pipx` as the command and `run trellio-mcp` as arguments.)*

### Using pip

```bash
pip install trellio-mcp
```

### From source

```bash
git clone https://github.com/scaratec/trellio-mcp.git
cd trellio-mcp
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Authentication

### Interactive (recommended)

Run the auth command on each machine to connect your Trello account:

If you installed globally (`pipx install` or `pip install`):
```bash
TRELLO_API_KEY=your_api_key trellio-mcp auth
```

If using on-the-fly execution (`pipx run`):
```bash
TRELLO_API_KEY=your_api_key pipx run trellio-mcp auth
```

This opens a browser where you authorize the app. The token
is captured automatically and stored in
`~/.config/trellio-mcp/credentials.json` (permissions 0600).

After auth, no environment variables are needed — the server
reads stored credentials on startup.

### Environment Variables (fallback)

If no stored credentials are found, the server falls back to
environment variables:

```bash
export TRELLO_API_KEY=your_api_key
export TRELLO_TOKEN=your_token
```

## MCP Client Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or `%APPDATA%\Claude\claude_desktop_config.json`
(Windows):

```json
{
  "mcpServers": {
    "trello": {
      "command": "pipx",
      "args": ["run", "trellio-mcp"]
    }
  }
}
```

If using env var auth instead of stored credentials, add:

```json
"env": {
  "TRELLO_API_KEY": "your_api_key",
  "TRELLO_TOKEN": "your_token"
}
```

### Claude Code

Add to `~/.claude/settings.json` or project
`.claude/settings.json`:

```json
{
  "mcpServers": {
    "trello": {
      "command": "pipx",
      "args": ["run", "trellio-mcp"]
    }
  }
}
```

### Gemini CLI

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "trello": {
      "command": "pipx",
      "args": ["run", "trellio-mcp"]
    }
  }
}
```

## Architecture

```
MCP Client (Claude / Gemini)
    │ stdio (JSON-RPC)
    ▼
trellio-mcp (FastMCP)
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
| 003 | Stored credentials with env var fallback |
| 004 | 1:1 tool mapping — one tool per trellio method |
| 005 | trellio as PyPI dependency (>=1.4.0) |
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
17 features passed, 0 failed, 0 skipped
163 scenarios passed, 0 failed, 0 skipped
970 steps passed, 0 failed, 0 skipped
```

Test architecture:
- `AsyncMock(spec=TrellioClient)` — mock at the client
  boundary, not HTTP
- Persistence validation via mock call records (§4.3)
- Anti-hardcoding via Scenario Outlines with >= 2 variants
  (§2.3)
- Layer-by-layer failure path enumeration (§4.5)
- Independent spec audit per §13

See [Case Study](docs/case-study-bdd-mcp-server.md) for a
detailed account of the BDD-driven development process.

## Project Structure

```
trellio-mcp/
├── src/trello_mcp/
│   ├── __init__.py        # Tool registration
│   ├── __main__.py        # Entry point (server + auth)
│   ├── server.py          # FastMCP instance + client mgmt
│   ├── auth.py            # OAuth flow + credential storage
│   ├── errors.py          # Error translation (ADR 007)
│   ├── tools/             # 10 modules, 48 tools
│   ├── resources.py       # 2 resource templates
│   └── prompts.py         # 3 prompts
├── features/              # 17 BDD feature files
│   └── steps/             # Step definitions
├── docs/
│   ├── adr/               # 7 Architecture Decision Records
│   ├── tool-design.md     # Scenario-driven tool analysis
│   └── case-study-bdd-mcp-server.md
└── pyproject.toml
```

## Publishing

### PyPI

```bash
uv build
twine upload dist/trellio_mcp-<version>*
```

### Smithery

Namespace is `gupta`. Update the release after a new PyPI version:

```bash
npx @smithery/cli mcp publish "https://github.com/scaratec/trellio-mcp" -n gupta/trellio-mcp
```

Also update the pinned version in `smithery.yaml` `commandFunction`.

## License

This project is licensed under the GNU General Public License
v3.0 — see the [LICENSE](LICENSE) file for details.
