# Limitation Records

A **Limitation Record (LIM)** documents an *accepted, bounded weakness* — a place where this project consciously lives with less than its [ADRs](../adr/) or the BDD Guidelines would otherwise demand.

The governance is not defined here. This register follows the framework in `burn-your-code/governance/limitations/`; the rules below are the parts a reader of *this* repository needs on hand.

## Default posture

> Every problem is solved cleanly per the ADRs and the BDD Guidelines. A Limitation Record is the documented exception, never the norm.

"Hard", "expensive" or "tedious" are not grounds for a record — they are grounds for doing the work. A record applies only where there is a demonstrable, substantive reason the clean path cannot be taken: a theoretical limit, an external dependency outside the project's control, or a scope boundary an ADR rules out explicitly.

## Governance

1. **No self-approval.** An implementer — including any agent — cannot unilaterally declare a limitation. A new record must be reviewed and explicitly approved by the project owner before it takes effect. Until then it stays at `Proposed`.
2. **No silent acceptance.** A limitation that is not in this directory does not exist. Code comments and commit messages do not substitute for a record; undocumented shortcuts are bugs.
3. **Every field is filled.** [`TEMPLATE.md`](TEMPLATE.md) is the minimum content. Empty fields block approval.

## For agents working in this repository

Before proposing a fix for a known-imperfect behaviour, check this register. A record here means the project has already weighed the clean solution and declined it — proposing that same solution again is noise, and implementing it silently contradicts an approved decision. If the record looks wrong, argue against the record; do not route around it.

## Lifecycle

```
Proposed -> Accepted -> (Mitigated -> Resolved)
                     -> Superseded by LIM-NNNN
         -> Withdrawn (paydown landed before approval)
```

Accepted records carry a mandatory **resolution intent**: `must-resolve` (a technical debt that is owed a paydown) or `permanent` (an architectural or theoretical boundary, no paydown owed). Resolved and Withdrawn records stay in the repository and in the index below; deleting a LIM file is non-conformant.

## Commit-message conventions

| Transition                | Commit verb                                              |
|---------------------------|----------------------------------------------------------|
| File a new LIM (Proposed) | `docs(scope): record LIM-NNNN — short title`             |
| Proposed → Accepted       | `docs(scope): accept LIM-NNNN [— short reason]`          |
| Accepted → Resolved       | `refactor(scope): resolve LIM-NNNN [via X]`              |
| Proposed → Withdrawn      | `refactor(scope): withdraw LIM-NNNN [— paid down via X]` |
| Accepted → Mitigated      | `docs(scope): note mitigation on LIM-NNNN [via X]`       |
| Accepted → Superseded     | `docs(scope): supersede LIM-NNNN by LIM-MMMM`            |

## Numbering & naming

`NNNN-short-kebab-case-title.md`, sequential from `0001`. Numbers are never reused.

## Index

| #    | Title | Status | Intent | Approved by |
|------|-------|--------|--------|-------------|
| 0001 | [The Smithery registry listing cannot be populated](0001-smithery-listing-cannot-be-populated.md) | Proposed | permanent | pending |

## Relationship to ADRs

[ADRs](../adr/) record decisions that shape the system; Limitation Records document accepted weaknesses within the chosen direction. An ADR can introduce a capability — a Limitation Record cannot. It only admits a gap, and references the ADRs whose clean implementation it bounds.
