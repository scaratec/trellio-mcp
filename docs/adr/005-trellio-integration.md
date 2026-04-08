# ADR 005: Trellio Library Integration

- **Status:** Accepted
- **Date:** 2026-04-08

## Context

The MCP server depends on the `trellio` library for all Trello API
interactions. The library lives in a separate repository at
`/home/randy/Projekte/privat/trellio`. The question is how to
manage this dependency.

Options considered:

1. **Local path import** -- `pip install -e ../trellio`
2. **Git dependency** -- `pip install git+file:///path/to/trellio`
3. **Vendored copy** -- copy `src/trellio/` into this repo

## Decision

We use a **Git dependency**.

## Rationale

**Versionable.** A git dependency pins to a specific commit or tag.
The MCP server's `requirements.txt` declares exactly which version
of trellio it was tested against:

```
trellio @ git+file:///home/randy/Projekte/privat/trellio@main
```

This prevents silent breakage when trellio changes. Upgrading is
an explicit act (update the ref), not an implicit side effect of
the library being editable.

**No code duplication.** Unlike vendoring, there is exactly one
copy of the trellio source code. Bug fixes in trellio propagate
to the MCP server when the dependency ref is updated.

**Clean dependency graph.** The MCP server's `requirements.txt`
declares trellio as a proper dependency alongside `mcp` and other
packages. Standard Python tooling (`pip freeze`, `pipdeptree`)
understands the relationship.

**Works without package publishing.** Unlike a PyPI dependency,
no package registry or publishing pipeline is needed. The git
repo is the source of truth.

## Trade-offs

**Local path coupling.** The `file:///` URL in requirements.txt
assumes a specific filesystem layout. Contributors must clone
trellio to the same relative location, or override the URL.

Mitigation: document the expected layout in README.md and provide
a `make setup` target that clones trellio if missing.

**No semantic versioning.** Git refs are commit hashes, not
semver. There is no automated way to detect breaking changes.

Mitigation: trellio's BDD suite (117 scenarios) serves as the
contract. If the MCP server's tests pass after updating the ref,
the integration is sound.

## Consequences

- `requirements.txt` includes a `git+file:///` line for trellio.
- The trellio repo must be cloned locally before installing deps.
- Updating trellio in the MCP server is: update the git ref in
  requirements.txt, reinstall, run tests.
- CI/CD (if any) needs access to the trellio repo.
