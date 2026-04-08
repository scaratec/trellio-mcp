# ADR 002: Transport Protocol

- **Status:** Accepted
- **Date:** 2026-04-08

## Context

MCP servers communicate with clients (Claude Desktop, Claude Code,
custom applications) via a transport layer. The protocol supports
multiple transports:

1. **stdio** -- Standard input/output. The client spawns the server
   as a child process and communicates via stdin/stdout.
2. **SSE (Server-Sent Events)** -- HTTP-based. The server runs as
   a persistent HTTP service, clients connect over the network.
3. **Streamable HTTP** -- Newer HTTP transport with request/response
   semantics, superseding SSE in the latest MCP spec.

## Decision

We use **stdio** as the sole transport.

## Rationale

**Standard for local MCP servers.** Claude Desktop and Claude Code
both launch MCP servers as child processes via stdio. This is the
default and most widely supported configuration. No network setup,
no port management, no TLS configuration.

**Security model.** stdio runs as a local process under the user's
own permissions. There is no network surface to attack, no
authentication layer to implement, no CORS to configure. The Trello
credentials (API key + token) remain in the local process
environment, never exposed over a network interface.

**Simplicity.** A stdio server is a single Python script that reads
from stdin and writes to stdout. No web framework, no HTTP server,
no process manager. The MCP SDK's `stdio_server()` context manager
handles all protocol framing.

**No multi-client requirement.** This server serves a single user's
Trello account. There is no use case for multiple concurrent clients
sharing one server instance, which would be the primary reason for
an HTTP transport.

## Consequences

- The server is started by the MCP client, not as a standalone
  daemon. It has no independent lifecycle.
- Configuration is via the client's MCP config (e.g.,
  `claude_desktop_config.json` or `.claude/settings.json`).
- Remote deployment requires wrapping in SSH or similar; native
  HTTP serving is not supported.
- If multi-client support is needed in the future, this decision
  must be revisited. Adding SSE transport is additive, not a
  rewrite -- the MCP SDK supports both on the same server object.
