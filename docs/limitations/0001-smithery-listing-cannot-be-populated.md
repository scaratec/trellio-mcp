# LIM 0001: The Smithery registry listing cannot be populated

- **Status:** Proposed
- **Resolution intent:** permanent (architectural boundary)
- **Date proposed:** 2026-07-30
- **Date approved:** pending — project-owner review required before Accepted
- **Date resolved:** not resolved
- **Date withdrawn:** not withdrawn
- **Proposed by:** the agent
- **Approved by:** pending — project-owner review required before Accepted
- **Resolution commit:** not resolved
- **Withdrawal commit:** not withdrawn
- **Scope:** Distribution and discovery — `smithery.yaml`, the Smithery badge and install command in `README.md`
- **Related ADRs:** [ADR-002](../adr/002-transport-protocol.md)
- **Related Guidelines:** BDD Guidelines §7.1 (deterministic mocks instead of uncontrolled live dependencies), §1.2 (visible behaviour instead of internal assumption)

## Resolution intent

`permanent`.

The barrier is [ADR-002](../adr/002-transport-protocol.md), which makes stdio the *sole* transport and names the absence of a network surface as part of the security model. Smithery populates a registry entry by connecting to the server over HTTP. Those two are not reconcilable by paying down debt: closing the gap requires the project to gain a capability it has deliberately decided not to have.

A Limitation Record cannot introduce that capability — only a new ADR superseding ADR-002 could. Until such an ADR exists, no paydown is owed, and this record documents a boundary rather than an IOU.

## Context

`smithery.yaml` has been in the repository since 2026-04-16 (commit `e92196c`). It declares `startCommand: {type: stdio}` and a `configSchema` requiring `trelloApiKey` and `trelloToken`, and its `commandFunction` returns `uvx trellio-mcp==<version>`. `README.md` carries a Smithery badge and offers `npx @smithery/cli install gupta/trellio-mcp --client claude` as the *first* installation option, above pipx and uvx.

Smithery distinguishes *hosted* servers (it runs them) from *external* servers (it only catalogues them). trellio-mcp is published as external. For an external entry, Smithery fills in description, connections, tool list and configuration schema by contacting the server itself and running an MCP initialisation handshake over HTTP.

On 2026-07-30 a publish was performed against namespace `gupta` (release `52f67d6b-bd83-4630-b8fd-ac7ae25f9403`). The registry accepted the release. The deploy log then reported:

```
[scan] Connection error: Initialization failed with status 422.
Your server could not be automatically scanned.
```

ADR-002 states the clean outcome that cannot be reached here: an HTTP transport would make the entry scannable, and the ADR rules it out on purpose ("no network surface to attack, no authentication layer to implement"). The consequences section of that ADR already anticipates the shape of this problem — "remote deployment requires wrapping in SSH or similar; native HTTP serving is not supported".

## Nature of the weakness

The registry entry `gupta/trellio-mcp` exists but carries no usable content. As of 2026-07-30, `GET https://registry.smithery.ai/servers/gupta/trellio-mcp` returns:

```json
{"qualifiedName":"gupta/trellio-mcp","displayName":"trellio-mcp","description":"",
 "iconUrl":null,"remote":false,"deploymentUrl":null,"connections":[],
 "security":null,"tools":null,"resources":null,"prompts":null}
```

Concretely missing, under the condition that the server is published as an external stdio server:

- `connections: []` — no client can derive a launch command from the entry. The `commandFunction` in `smithery.yaml` is never surfaced.
- `tools: null` — none of the server's tools are discoverable through Smithery search.
- `description: ""` — the entry is invisible to full-text search on the registry; a search for "trello" or "trellio" does not return it.

The observable consequence is that every artefact pointing at Smithery — the README badge, the README install command, and `smithery.yaml` itself — advertises an install path that cannot work, while the publish step reports success.

A populated external entry looks different in every one of these fields; `offshoreproz/agent-company`, for comparison, returns a 2226-character description, one connection, eleven tools, `remote: true` and a non-null `deploymentUrl`.

## Why the clean solution is not chosen

Two of the acceptable grounds apply, and they reinforce each other.

**An explicit scope boundary from an ADR.** Making the entry scannable means exposing an HTTP endpoint that answers an MCP initialisation handshake — either by deploying the server as a hosted/remote service, or by publishing a server card at a stable URL. ADR-002 chose stdio as the sole transport and counts the absent network surface as a security property, not an omission. Building an HTTP surface solely so that a catalogue can introspect the server inverts that decision for a discovery benefit.

**An external dependency outside project control.** The scan is Smithery's mechanism, on Smithery's infrastructure, with an error surface the project cannot influence: the publish succeeds, the scan fails asynchronously, and the resulting empty entry is indistinguishable from one that has not been published at all. There is no supported way to hand Smithery a static manifest for a stdio-only server, and no way to make the 422 visible to a user who arrives via the badge.

What is explicitly *not* the reason: effort. Publishing itself is a single command and was performed successfully. The gap is structural, not a matter of remaining work.

## Mitigations in place

- **PyPI is the working distribution channel, verified end to end.** Release 0.14.1 is live; a clean-`HOME` `uvx --with trellio-mcp==0.14.1` resolves `mcp 1.29.0` and imports the server module successfully. Every documented non-Smithery install path (`pipx install trellio-mcp`, `uvx trellio-mcp`, the `.mcp.json` entry) goes through it.
- **The install path that does work is guarded by an executable test.** `features/dependency_compatibility.feature` builds a wheel, installs it into throwaway environments at both ends of the declared `mcp` range and drives the resulting server over stdio. It carries no opt-in tag, so a regression in the channel users actually use fails the default suite.
- **A second catalogue is targeted that does not require a scan.** `server.json` describes the server for the official MCP registry with `registryType: pypi` and `transport: stdio`, i.e. by static declaration rather than introspection. It is kept at the released version (0.14.1).
- **The pinned version in `smithery.yaml` is updated at every release** alongside `pyproject.toml` and `server.json`, so that if the scan barrier ever disappears the entry does not come up advertising a stale version. (It had drifted to 0.12.0 across two releases before 0.14.1; that drift is now part of the release checklist.)
- **The broken install path is no longer advertised.** The Smithery badge and the `npx @smithery/cli install` command have been removed from the Installation section of `README.md`; pipx is now the first option offered. A user cannot walk into the failure from the README.
- **The Publishing section names this record.** The Smithery publish command is retained there — it is the correct command, and it succeeds — with an adjacent note that the resulting listing stays empty and a link to this record. A maintainer who runs it is told in advance what to expect, which is the loop this record exists to break.
- **The README points agents at the register.** The architecture section states that accepted weaknesses live in `docs/limitations/` and that the register is to be consulted before proposing a fix for a known-imperfect behaviour.

## Residual risk

A user who browses Smithery rather than the repository finds `gupta/trellio-mcp` — the entry is listed, it just has nothing in it — and runs `npx @smithery/cli install gupta/trellio-mcp --client claude`. The CLI resolves an entry whose `connections` array is empty, so there is no launch command and no `configSchema` to prompt against. The client is left either without a server entry at all, or with one that never receives `TRELLO_API_KEY` and `TRELLO_TOKEN` — and the resulting failure surfaces at startup as a missing-Trello-credentials error. Nothing in that error mentions Smithery, the registry, or a failed scan. Removing the badge from `README.md` closes the path *from* the repository; it does not remove the entry from Smithery, and only Smithery can do that.

The same applies internally, and has already cost time: the empty listing sat unnoticed from 2026-04-16 to 2026-07-30 because publishing reports success, and diagnosing it required comparing the registry JSON against a working third-party entry field by field. Without this record, the next person to touch the release process — human or agent — re-runs `npx @smithery/cli mcp publish`, sees it succeed, and repeats the investigation from scratch.

There is a second-order risk on the agent side that this register is meant to cover: an agent asked to "fix the Smithery listing" will otherwise propose adding an HTTP or SSE transport, which silently contradicts ADR-002.

## Triggers for revisit

- Smithery supports registering a stdio-only external server without an HTTP scan — for example by accepting `smithery.yaml`'s `commandFunction` directly, or by allowing a manifest upload equivalent to `server.json`.
- A new ADR supersedes ADR-002 and adds an HTTP or streamable-HTTP transport for reasons of its own. The scan barrier then falls away as a side effect and this record must be re-examined rather than left standing.
- The official MCP registry entry (`server.json`) also fails to publish or populate, leaving PyPI as the only catalogue. The cost/benefit of a hosted variant changes materially at that point.
- Any user-reported installation failure that traces back to the Smithery listing.
- The badge or the `npx @smithery/cli install` command is reinstated in `README.md` while this record still stands.

## References

- [ADR-002: Transport Protocol](../adr/002-transport-protocol.md) — stdio as the sole transport.
- [ADR-001: MCP SDK and Implementation Language](../adr/001-mcp-sdk-and-language.md) — the Python `mcp` SDK, whose `stdio_server()` is the transport in use.
- BDD Guidelines §7.1 — live systems belong in a few targeted integration tests; the Smithery registry is an uncontrolled live dependency and is deliberately not covered by the suite.
- BDD Guidelines §1.2 — the suite validates externally observable behaviour of the *server*; the state of a third-party catalogue entry is not such behaviour.
- `smithery.yaml`, added 2026-04-16 in commit `e92196c`.
- Smithery release `52f67d6b-bd83-4630-b8fd-ac7ae25f9403` (2026-07-30) — accepted, scan failed with HTTP 422.
- Registry state at the time of filing: `GET https://registry.smithery.ai/servers/gupta/trellio-mcp`.
- Smithery configuration reference: <https://smithery.ai/docs/config#smitheryyaml>
