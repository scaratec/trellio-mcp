# ADR 004: Tool Granularity

- **Status:** Accepted
- **Date:** 2026-04-08

## Context

The MCP server exposes Trello operations as tools that an LLM can
invoke. The trellio library provides 38 client methods across 10
resource types. The question is how these map to MCP tools:

1. **1:1 mapping** -- one tool per client method (38 tools)
2. **Grouped by resource** -- one tool per resource with an
   `action` parameter (~12 tools)
3. **Hybrid** -- frequent operations as individual tools, rest
   grouped

## Decision

We use a **1:1 mapping**: one MCP tool per trellio client method.

## Rationale

**LLM usability.** LLMs perform better with tools that have a
single, clear purpose and a small parameter set. A tool named
`create_card` with parameters `list_id` and `name` is
unambiguous. A tool named `card_operations` with parameters
`action`, `card_id`, `list_id`, `name`, `desc` -- where most
params are conditionally required depending on `action` -- forces
the LLM to reason about parameter validity, increasing error
rates.

**Schema clarity.** Each tool has its own JSON Schema with
exactly the parameters it needs. `create_board` requires `name`.
`delete_board` requires `board_id`. `search` requires `query`.
There is no parameter overloading, no conditional requirements,
no unused fields.

**Discoverability.** When a client lists available tools, 38
well-named tools form a readable API surface:

```
create_board, list_boards, get_board, update_board, delete_board,
create_card, list_cards, get_card, update_card, delete_card,
search, create_webhook, ...
```

Each name is self-documenting. The LLM can pick the right tool
from the name alone without reading descriptions.

**Thin handlers.** Each tool handler is a 3-5 line function:
validate input, call trellio method, format response. No
dispatch logic, no action routing, no parameter validation
beyond what the schema already enforces.

## Trade-offs

**Tool count.** 38 tools is above the typical range for MCP
servers (5-20). This increases the system prompt size when the
client injects tool descriptions. However:

- Modern LLMs handle 30-50 tools without degradation
- Claude specifically is optimized for large tool sets
- Each tool description is 1-2 sentences, not paragraphs
- The alternative (fewer tools with complex schemas) trades
  tool count for per-tool complexity, which is worse for LLMs

**Naming consistency.** With 38 tools, naming must be rigorous.
We use the pattern `{verb}_{resource}` consistently:

- `create_board`, `list_boards`, `get_board`, `update_board`,
  `delete_board`
- `create_card`, `list_cards`, `get_card`, `update_card`,
  `delete_card`
- `add_comment`, `list_comments`, `update_comment`,
  `delete_comment`
- `search` (standalone, no resource suffix)

## Consequences

- Every trellio client method has a corresponding MCP tool.
- Adding a new trellio method requires adding a new MCP tool
  (mechanical, not architectural).
- Tool descriptions must be concise (1 sentence) to keep the
  system prompt manageable.
- The server's `list_tools` response is large but structured.
