# ADR 006: MCP Capabilities (Tools, Resources, Prompts)

- **Status:** Accepted
- **Date:** 2026-04-08

## Context

The MCP protocol defines three capability types:

1. **Tools** -- Functions the LLM can invoke (side effects allowed)
2. **Resources** -- Data the LLM can read (read-only context)
3. **Prompts** -- Pre-built prompt templates the user can invoke

The question is which capabilities this server should expose.

## Decision

We expose **all three**: Tools, Resources, and Prompts.

## Rationale

### Tools (write + read operations)

All 38 trellio client methods become MCP tools. This is the core
of the server. Tools handle both read and write operations because
the LLM needs to invoke them dynamically based on user intent.

### Resources (structured read-only context)

Resources provide a way for the LLM to pull Trello data into its
context *without* a tool call. This is useful for:

- **Board overview** -- `trello://board/{id}` returns board
  details including lists and card counts. The LLM can reference
  this as context for planning or summarization tasks.
- **Card detail** -- `trello://card/{id}` returns card with
  checklists, comments, and attachments. Richer than the tool
  response, which returns just the card object.

Resources are read-only by protocol definition. They do not
replace tools -- they complement them by providing richer context
that would be awkward to assemble from multiple tool calls.

**Resource templates** use URI patterns with parameters:

```
trello://board/{board_id}
trello://card/{card_id}
```

The client resolves these by calling multiple trellio methods
(get_board + list_lists + list_cards) and composing a unified
response.

### Prompts (user-facing workflows)

Prompts are pre-built templates that guide the LLM toward
specific Trello workflows:

- **summarize_board** -- "Summarize the current state of board
  {board_id} including open cards per list and blockers."
- **create_sprint** -- "Create a new sprint board with lists
  To Do, In Progress, Review, Done and populate it with cards
  from {source}."
- **daily_standup** -- "Generate a standup report based on
  cards moved in the last 24 hours on board {board_id}."

Prompts are optional convenience features. They don't add new
functionality -- everything they do could be done with tools.
Their value is in reducing the user's effort to express common
workflows.

## Architecture

```
MCP Server
├── Tools (38)           # 1:1 with trellio methods
│   ├── create_board     # write operations
│   ├── search           # read operations
│   └── ...
├── Resources (2 templates)
│   ├── trello://board/{board_id}  # aggregated board view
│   └── trello://card/{card_id}    # aggregated card view
└── Prompts (3)
    ├── summarize_board  # board status summary
    ├── create_sprint    # sprint setup workflow
    └── daily_standup    # standup report generation
```

## Consequences

- The server registers tools, resource templates, and prompts
  at startup.
- Resources require aggregation logic (multiple trellio calls
  composed into a single response). This is the only place
  where the MCP server has "business logic" beyond delegation.
- Prompts are static templates with parameter substitution.
  They are cheap to add and maintain.
- The server's `initialize` response advertises all three
  capabilities, which some older MCP clients may not support.
  stdio clients (Claude Desktop, Claude Code) support all three.
