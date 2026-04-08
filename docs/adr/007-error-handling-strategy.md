# ADR 007: Error Handling Strategy

- **Status:** Accepted
- **Date:** 2026-04-08

## Context

When a tool call fails (Trello API error, validation error,
timeout), the MCP server must communicate the failure to both:

1. **The MCP client** (Claude Desktop, Claude Code) -- needs to
   know the call failed for protocol-level handling.
2. **The LLM** -- needs to understand what went wrong so it can
   explain the error to the user or retry with different params.

The MCP protocol provides two mechanisms:

- `isError: true` on the tool result -- signals the client
- `content` text in the tool result -- read by the LLM

## Decision

We use **both mechanisms combined**: `isError=true` for the client
plus a structured error description in the content for the LLM.

## Rationale

**isError flag for the client.** The MCP client uses this flag to
decide whether to show error UI, log the failure, or adjust its
behavior. Without it, the client treats a failed tool call as a
successful one that returned an error-like string -- which breaks
error tracking and monitoring.

**Structured content for the LLM.** The LLM reads the tool
result's content to decide what to tell the user. A structured
error message helps it give actionable feedback:

```json
{
  "error": "Board not found",
  "status_code": 404,
  "suggestion": "The board ID may be incorrect. Use list_boards to find valid board IDs."
}
```

This is better than a raw status code because it includes context
the LLM can relay to the user.

## Implementation

All tool handlers follow this pattern:

```python
@server.tool()
async def get_board(board_id: str) -> list[TextContent]:
    try:
        board = await client.get_board(board_id)
        return [TextContent(type="text", text=board.model_dump_json())]
    except TrelloAPIError as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Trello API error {e.status_code}: {e.message}"
            )
        )
```

### Error categories and their handling

| Error Type | status_code | isError | LLM Message |
|---|---|---|---|
| Resource not found | 404 | true | "X not found. Use list_X to find valid IDs." |
| Validation error | 400 | true | "Invalid input: {detail}" |
| Auth failure | 401 | true | "Authentication failed. Check TRELLO_API_KEY and TRELLO_TOKEN." |
| Rate limited | 429 | true | "Rate limited by Trello. The request was retried {n} times." |
| Server error | 5xx | true | "Trello server error. Try again later." |
| Timeout | 0 | true | "Request timed out after {n}s." |

Note: trellio already retries 429/5xx with backoff. If the error
reaches the MCP layer, retries are exhausted.

## Consequences

- Every tool handler has a try/except for TrelloAPIError.
- The error content is a JSON string readable by the LLM.
- The isError flag propagates to the MCP client for monitoring.
- No tool call silently fails -- every error path is explicit.
- The suggestion field in 404 errors guides the LLM toward
  self-correction (e.g., listing resources before operating).
