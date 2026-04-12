# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
| < 0.1   | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in trellio-mcp, please
report it responsibly:

- **Email:** gupta@scaratec.com
- **Response time:** We aim to acknowledge reports within 48 hours.
- **Disclosure:** Please do not open a public issue for security
  vulnerabilities. We will coordinate disclosure after a fix is
  available.

Include in your report:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Security Model

### Architecture

trellio-mcp is a **Model Context Protocol (MCP) server** that
bridges AI agents (Claude, Gemini) to the Trello API. It runs as a
local subprocess communicating via **stdio** (JSON-RPC over
stdin/stdout). There is no network listener in normal operation.

```
MCP Client (Claude/Gemini)
    |  stdio (JSON-RPC)
    v
trellio-mcp (FastMCP)
    |  HTTPS
    v
Trello API (api.trello.com)
```

### Threat Model

| Threat                      | Mitigation                                     |
|-----------------------------|-------------------------------------------------|
| Credential theft            | Stored at `~/.config/trellio-mcp/credentials.json` with mode 0600; directory mode 0700 |
| Man-in-the-middle           | All Trello API calls use HTTPS via trellio-client |
| Code injection              | No eval/exec/subprocess; tool inputs passed as typed parameters |
| Supply chain compromise     | 2 direct dependencies; pin versions in production |
| Unauthorized data access    | OAuth token scoped to authenticated Trello user |
| Prompt injection via tools  | Tools return structured JSON; errors use `isError=true` flag |

### Authentication

trellio-mcp supports two authentication methods:

1. **Interactive OAuth flow** (`trellio-mcp auth`): Opens browser,
   captures token via localhost callback, stores credentials with
   restrictive file permissions.
2. **Environment variables**: `TRELLO_API_KEY` and `TRELLO_TOKEN`
   for CI/headless environments.

### Credential Storage

- **Path:** `~/.config/trellio-mcp/credentials.json`
- **Directory permissions:** `0o700` (owner only)
- **File permissions:** `0o600` (owner read/write only)
- **Format:** JSON with `api_key` and `token` fields
- **Encryption at rest:** Not implemented (see audit report)

### Permissions Scope

The OAuth token is issued with:
- **Scope:** `read,write` (required for full tool coverage)
- **Expiration:** `never` (see audit report for recommendation)

### What trellio-mcp Does NOT Do

- Does not open network ports (stdio transport only)
- Does not execute dynamic code (no eval, exec, subprocess)
- Does not persist Trello data beyond the current tool invocation
- Does not log API keys or tokens
- Does not send telemetry, analytics, or tracking data
- Does not access files outside `~/.config/trellio-mcp/`
