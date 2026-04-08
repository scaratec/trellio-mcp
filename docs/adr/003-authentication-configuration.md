# ADR 003: Authentication Configuration

- **Status:** Accepted
- **Date:** 2026-04-08

## Context

The MCP server needs Trello API credentials (API Key and Token) to
authenticate requests via the trellio library. These credentials
must be configured at server startup. Options considered:

1. **Environment variables** -- `TRELLO_API_KEY`, `TRELLO_TOKEN`
2. **.env file** with python-dotenv fallback
3. **MCP config** -- credentials in `claude_desktop_config.json`

## Decision

We use **environment variables** exclusively.

## Rationale

**12-Factor compliance.** Configuration via environment variables
is the standard for process-level configuration. It works
identically in development (shell export), CI (pipeline secrets),
and production (orchestrator env injection).

**Security.** Environment variables are not committed to version
control. They are scoped to the process and its children. This is
safer than a `.env` file (which can accidentally be committed) and
safer than MCP config JSON (which is stored in plaintext in the
user's config directory).

**MCP client integration.** Both Claude Desktop and Claude Code
support `env` blocks in their MCP server configuration:

```json
{
  "mcpServers": {
    "trello": {
      "command": "python",
      "args": ["-m", "trello_mcp"],
      "env": {
        "TRELLO_API_KEY": "your_key",
        "TRELLO_TOKEN": "your_token"
      }
    }
  }
}
```

This means the user configures credentials once in their MCP
client config, and they are injected as environment variables
into the server process. No additional configuration mechanism
is needed.

**No additional dependency.** python-dotenv is unnecessary. The
MCP client's `env` block provides the same convenience for local
development.

## Implementation

The server reads credentials at startup and fails fast with a
clear error message if either variable is missing:

```python
api_key = os.environ.get("TRELLO_API_KEY")
token = os.environ.get("TRELLO_TOKEN")
if not api_key or not token:
    raise SystemExit(
        "TRELLO_API_KEY and TRELLO_TOKEN environment "
        "variables are required"
    )
```

## Consequences

- No `.env` file support. Users who want dotenv must source it
  themselves (`source .env && python -m trello_mcp`).
- No runtime credential rotation. Changing credentials requires
  restarting the server process.
- Credentials are visible in `/proc/<pid>/environ` on Linux.
  This is acceptable for a local stdio server running under the
  user's own session.
