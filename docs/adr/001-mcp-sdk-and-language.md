# ADR 001: MCP SDK and Implementation Language

- **Status:** Accepted
- **Date:** 2026-04-08

## Context

We are building an MCP (Model Context Protocol) server that exposes
Trello API operations as tools for LLM-based assistants. The server
needs to integrate with the `trellio` library, an async Python
Trello client built on httpx and pydantic.

Three SDK options were evaluated:

1. **Python `mcp` SDK** -- Anthropic's official Python MCP SDK
2. **TypeScript `@modelcontextprotocol/sdk`** -- official TS SDK
3. **Python `claude-agent-sdk`** -- Anthropic's Agent SDK

## Decision

We use the **official Python `mcp` SDK**.

## Rationale

**Language alignment.** The `trellio` library is Python/async. Using
the Python MCP SDK eliminates cross-language bridging. Tool handlers
can directly `await` trellio methods without subprocess calls,
HTTP proxying, or serialization layers.

**Async compatibility.** The Python MCP SDK supports async handlers
natively. Trellio's `TrellioClient` is fully async (httpx). This
means tool handlers are simple one-liner delegations:

```python
@server.tool()
async def create_board(name: str) -> str:
    board = await client.create_board(name)
    return board.model_dump_json()
```

No thread pools, no `asyncio.run()` wrappers, no callback
translation.

**Ecosystem fit.** The TypeScript SDK has a larger ecosystem of
community MCP servers, but our use case is narrow (one specific
API integration) and doesn't benefit from ecosystem breadth. The
Agent SDK is designed for multi-step agentic workflows, which adds
unnecessary complexity for a stateless tool server.

**Deployment simplicity.** A single Python process serves both the
MCP protocol and the Trello API calls. No polyglot runtime, no
multi-process coordination.

## Consequences

- The MCP server is a Python package requiring Python 3.10+.
- All tool handlers are async functions.
- The `mcp` package must be added to project dependencies.
- Contributors need Python experience, not TypeScript.
- We inherit the Python MCP SDK's protocol support and any
  limitations (e.g., feature parity with the TS SDK may lag).
