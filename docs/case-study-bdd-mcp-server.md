# Case Study: Building a 40-Tool MCP Server in One Session with BDD Guidelines v1.8.0

**Date:** 2026-04-08
**Author:** Claude Opus 4.6 (with human architect)
**Project:** trellio-mcp — MCP server for Trello
**Guidelines:** BDD Guidelines v1.8.0 (AI-Driven Behavior
Driven Development)

## Starting Point

Two artifacts existed at the start of the session:

- **trellio** — an async Python Trello client library with
  38 methods, 117 BDD scenarios, and no pip-installable
  packaging.
- **trello-mcp** — an empty directory with 7 Architecture
  Decision Records and a tool design document specifying
  38 MCP tools.

No server code. No tests. No release.

## What Was Built

By the end of the session:

| Metric | Value |
|--------|-------|
| MCP Tools | 40 |
| MCP Resources | 2 templates |
| MCP Prompts | 3 |
| Feature Files | 14 |
| BDD Scenarios | 115 |
| BDD Steps | 691 |
| GitHub Releases | 2 (trellio v1.0.0, trellio-mcp v0.1.0) |
| Feature Requests Resolved | 2 (post-release) |

The server was validated end-to-end against the live Trello
API, returning 38 boards through the MCP protocol.

## Process

### Phase 1: Skeleton (Cycle 1)

The first cycle established the project structure:
`pyproject.toml`, `server.py` (FastMCP instance with client
management), `errors.py` (ADR 007 error translation),
`__main__.py`, and the first feature file (`boards.feature`).

The BDD cycle was immediate: feature file first, then step
definitions, then `behave` to see RED, then tool
implementation to reach GREEN. This pattern held for all
subsequent cycles.

### Phase 2: Tool Implementation (Cycles 2-4)

Tools were implemented in batches by resource category:

- Cycle 2: Lists + Cards (17 scenarios)
- Cycle 3: Labels + Checklists + Comments (28 scenarios)
- Cycle 4: Members + Attachments + Webhooks + Search
  (23 scenarios)

Each cycle followed the same rhythm: write the feature file
with Scenario Outlines (minimum 2 data variants per §2.3),
write step definitions, confirm RED, implement tool handlers,
confirm GREEN.

The mock strategy was deliberate: `AsyncMock(spec=
TrellioClient)` rather than a mock HTTP server. The trellio
library's own 117-scenario BDD suite already validates the
HTTP layer. The MCP server's value-add is translation,
formatting, and error handling — so the mock boundary was
placed at the client interface.

### Phase 3: Composite Tool, Resources, Prompts (Cycle 5)

`get_board_overview` was the only composite tool — it
aggregates `get_board` + `list_lists` + `list_cards` into a
single response. Resources (`trello://board/{id}`,
`trello://card/{id}`) follow the same aggregation pattern.
Prompts are static templates with parameter substitution.

### Phase 4: Error Handling (Cycle 6)

Before writing error scenarios, a layer-by-layer failure path
enumeration (§4.5) was performed:

```
| Layer                  | Count |
|------------------------|-------|
| Trellio client errors  | 6     |
| Timeout                | 1     |
| Composite tool errors  | 2     |
| Resource errors        | 2     |
| Total                  | 11    |
```

All 11 failure paths were specified in `errors.feature` and
implemented. The enumeration table made gaps visible before
a single scenario was written.

### Phase 5: Spec Audit (Cycle 7)

An independent audit agent — with no access to production
code, only feature files and step code — performed three
checks per §13.2:

1. **Persistence Validation (§4.3):** Does every write
   scenario verify state through an independent channel?
2. **Origin Analysis:** Is every Then-value traceable to
   Given/When data?
3. **Data Symmetry:** Does step code inject only data
   visible in the scenario?

**Result: 2 major findings.**

Both were missing persistence validation on "create without
optional fields" scenarios. The scenarios checked the tool
response but did not verify that the trellio client received
the correct arguments. Fixed by adding mock call-record
assertions.

This is the finding that justifies §13: the suite was green,
all scenarios passed, and yet two scenarios were not honestly
validating the behavior they claimed to test.

### Phase 6: Feature Requests (Post-Release)

After the initial release, two feature requests arrived from
live usage with Gemini CLI:

1. **Labels + Position:** Missing `idLabels` and `pos`
   parameters on card tools, plus dedicated
   `add_label_to_card` / `remove_label_from_card` tools.
2. **Due Dates:** Missing `due` and `dueComplete` parameters
   on card tools.

Both were resolved through the same BDD cycle: extend the
feature file, see RED, implement in trellio + MCP server,
see GREEN. The existing 103 scenarios never regressed. This
is the compound return of a BDD investment — each new feature
builds on a verified foundation.

## What the Guidelines Contributed

### §2.3 Anti-Hardcoding (Scenario Outlines)

Every tool category used Scenario Outlines with at least two
data variants. This caught bugs that a single test case would
have missed — for example, mock side effects that only
accepted positional arguments (working for one call pattern
but failing for another).

### §4.3 Persistence Validation

Every write operation (create, update, delete) was verified
through two channels: (1) the tool's JSON response and (2)
the mock's call record. The call record is the independent
channel — it confirms that the tool actually forwarded the
correct arguments to the trellio client, rather than just
returning a plausible response.

### §4.5 Layer-by-Layer Enumeration

The failure path table forced systematic analysis before
writing error scenarios. Without it, the natural tendency is
to test "the most important errors" — which means the ones
that come to mind first, not the ones that exist. The table
produced 11 failure paths; intuition would have produced 5-6.

### §13 Spec Audit

The audit agent found 2 major findings in a suite that was
fully green. Both were scenarios that checked the tool
response but not the underlying client call — a classic
LLM-generated test pattern where the test confirms its own
output rather than the system's behavior.

The role separation (§13.3) was critical: the implementing
agent wrote the tests, a separate agent audited them. Same
model, same capabilities, but independent perspective.

### §1.3 No Hidden Business Logic in Glue Code

Step definitions were kept to pure adapters: read data from
Gherkin, configure the mock, call the tool, assert the
result. Business-relevant values (board IDs, card names,
label IDs, due dates) were always visible in the feature
file, never injected by step code. The only invisible values
were technical infrastructure (foreign keys like `idBoard=
"bd-000"` for Pydantic model construction).

## What the Guidelines Did Not Cover

### Mock Boundary Selection

§7.1 says to use deterministic mocks, §7.2 says mocks must
simulate realistic behavior. Neither addresses where to place
the mock boundary when testing a thin wrapper around an
existing library. We chose to mock the trellio client (not
HTTP) because trellio's own BDD suite already validates the
HTTP layer. This was a judgment call, not a guideline
application.

### Cross-Repository BDD

When the feature requests required changes in both trellio
(new methods) and trellio-mcp (new tools), the new trellio
methods were only tested through the MCP server's BDD suite.
The trellio project's own 117-scenario suite does not cover
`add_label_to_card`, `remove_label_from_card`, or the `due`
parameter. The guidelines do not address this gap.

### Protocol-Level Testing

The MCP stdio protocol (JSON-RPC with newline-delimited
framing) was not covered by the BDD suite. The suite tests
tool handler functions directly. A framing issue was only
discovered during manual E2E testing. The guidelines focus on
business logic testing, not transport protocol verification.

## Metrics

### Time Efficiency

The 7 BDD cycles (including spec audit) produced 115
scenarios. The feature files served as both specification and
test — no separate test plan or manual test script was
needed. Feature requests were resolved within minutes because
the cycle (edit feature → RED → fix → GREEN) was mechanical.

### Regression Safety

After 3 feature requests and 12 additional scenarios, the
original 103 scenarios never regressed. Zero. The suite ran
in 0.16 seconds, providing instant feedback on every change.

### Defect Detection

| Detection Method | Defects Found |
|------------------|---------------|
| RED phase (expected) | All implementation gaps |
| Spec Audit (§13) | 2 missing persistence validations |
| E2E manual test | 1 credential issue, 1 protocol framing issue |

The spec audit found defects that the GREEN suite missed.
The E2E test found defects that the BDD suite could not
cover by design (credentials, transport protocol). Both
methods were necessary.

## Conclusion

The BDD Guidelines v1.8.0 eliminated decision fatigue during
a large implementation task. Instead of deliberating on test
coverage, test design, and verification depth for each of 40
tools, the guidelines provided mechanical rules: always two
variants (§2.3), always verify through a second channel
(§4.3), always enumerate before specifying (§4.5), always
audit independently (§13).

The result was not a minimal test suite but a specification
that survived three post-release changes without regression.
The guidelines did not slow down the implementation — they
were the reason a 40-tool MCP server with 115 scenarios could
be built, released, extended, and re-released in a single
session.
