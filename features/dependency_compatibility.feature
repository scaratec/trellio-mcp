Feature: Dependency Compatibility and Server Startup
  As a user installing trellio-mcp via uvx or pip
  I want the server to start and serve MCP requests
  So that my MCP client can actually reach the Trello tools

  # Why this feature exists:
  #
  # The rest of the suite imports the tool functions directly against
  # whatever versions the local .venv or uv.lock happens to hold. It
  # therefore cannot see a broken dependency declaration: the suite stays
  # green while every fresh install of the published package fails.
  #
  # A fresh install resolves from the constraints in pyproject.toml, not
  # from uv.lock — uv.lock is not shipped in the sdist or wheel. Any
  # resolution the declared constraints permit is a resolution a real
  # user will get. So the constraints, not the built artifact, are the
  # specification under test here, and the observable behaviour is: the
  # server starts and speaks MCP.
  #
  # What is installed is a wheel built from the working tree, not the
  # working tree itself. Installing the directory would be wrong twice
  # over: uv caches a local-directory build keyed on pyproject.toml, so a
  # change under src/ is served from a stale wheel and a source regression
  # becomes unobservable; and a directory install skips the packaging step,
  # so a file missing from the distribution goes unnoticed.
  #
  # The server is launched through its console entry point (the same one
  # uvx invokes), not via "python -m", so the entry-point metadata is
  # exercised on the path a real user takes.
  #
  # All dependencies resolve from PyPI. A local sibling checkout is
  # deliberately NOT injected: that would bypass the very version
  # constraints under test.
  #
  # Failure path enumeration (BDD Guidelines §4.5):
  #
  # | Layer                 | Fehlerquelle                             | Anzahl | Abgedeckt |
  # |-----------------------|------------------------------------------|--------|-----------|
  # | Dependency range      | Newest permitted / lowest supported mcp  | 2      | 2         |
  # | Server startup        | Process fails to serve, or exits non-zero| 1      | 1         |
  # | MCP protocol          | initialize handshake, tools/list         | 2      | 2         |
  # | Tool registry         | A registration module silently dropped   | 1      | 1         |
  # | Packaging             | Wheel builds; entry point resolves; a    |        |           |
  # |                       | module missing from the distribution     | 2      | 2         |
  # | Gesamt                |                                          | 8      | 8         |
  #
  # Deliberately NOT covered here, with reasons:
  #
  # | Layer          | Fehlerquelle                          | Warum nicht                          |
  # |----------------|---------------------------------------|--------------------------------------|
  # | Import         | Upstream removes/renames a module     | see note below — not expressible     |
  # | Resolution     | Oldest allowed TRANSITIVE versions    | floors a certifi from the py2 era    |
  # | Interpreter    | Oldest/newest supported Python        | needs a CI matrix, not one host      |
  # | Packaging      | sdist (as opposed to wheel) contents  | wheel is the artifact uvx installs   |
  # | Tool execution | Break visible only on a real API call | needs live Trello; see errors.feature|
  # | Startup        | Exit AFTER serving vs BEFORE serving  | one exit code, not two causes        |
  #
  # On the "upstream removes a module" row: that is the defect this
  # feature was written for (mcp 2.0 dropped mcp.server.fastmcp). It has
  # no scenario of its own because it cannot be stated as one — pinning a
  # known-incompatible version produces a resolver conflict, not an
  # import error, so there is no observable server behaviour to assert.
  # It is covered indirectly and unavoidably: whenever the declared
  # constraints permit such a version, the "highest" rows below fail.
  # That indirection is the reason this feature must run by default.
  #
  # Credentials are out of scope: the handshake and tools/list never
  # reach the Trello API. Credential and API failures are covered by
  # auth.feature and errors.feature. The server is deliberately run with
  # no credential source at all — see the Background — so that a
  # developer's real ~/.config/trellio-mcp/credentials.json can never be
  # picked up by this feature.
  #
  # Note on determinism: the "highest" strategy resolves against PyPI at
  # run time, so this feature requires network access and is intentionally
  # time-dependent — it is a canary for upstream releases. A failure here
  # means an upstream dependency changed, not necessarily that this
  # repository regressed. It carries no opt-in tag: a dependency guard
  # that must be asked for is not a guard, since the regression it catches
  # is exactly the one nobody thinks to look for.

  Background:
    Given the trellio-mcp package built as a distributable wheel
      And the package declares a lowest supported mcp version of "1.12.0"
      And the package declares an mcp upper bound of "2.0.0"
      And the server has no Trello credentials available

  # --- Both ends of the declared mcp range (§2.3 Varianz) ---
  #
  # The defect this feature exists for was a range that permitted a version
  # the code cannot import. So both ends of the range are installed:
  #   newest permitted  -> whatever the upper bound currently allows
  #   lowest supported  -> the declared floor
  # Both are real installations a user can get. Both must start. A range
  # that only works at one end is mis-declared.
  #
  # Only mcp is pinned; every other dependency stays at its newest
  # compatible version. Driving all transitive dependencies to their floors
  # instead would fail on a decade-old certifi, which says nothing about
  # this package — see the exclusion table above.
  #
  # On the protocol version: MCP negotiates by echoing back the version
  # the client asked for when the server supports it. The requested
  # version is therefore stated in the When, and the Then asserts the
  # echo. This proves the MCP layer is live and answering — it does not
  # prove the server implements any particular protocol revision.

  Scenario Outline: Server starts at both ends of the declared mcp range
    When the package is installed with the <boundary> mcp version
      And an MCP client requesting protocol version "2024-11-05" connects to the installed server
    Then the server should complete the MCP initialize handshake
      And the server should confirm MCP protocol version "2024-11-05"
      And the server process should exit cleanly

    Examples:
      | boundary         |
      | newest permitted |
      | lowest supported |

  # --- Tools are actually served (§4.3 keine Silent Failures) ---
  #
  # A successful handshake alone does not prove the tool registry survived
  # the import. The registry is assembled from one module per Trello
  # domain, and each module is imported for its side effect; a single
  # failed or dropped import removes that module's tools while leaving the
  # server otherwise healthy. Asserting a total count would not catch that
  # — any threshold loose enough to survive refactoring is loose enough to
  # hide a whole module. So one tool per module is named instead.

  Scenario Outline: Server serves the tools of every registration module
    When the package is installed with the <boundary> mcp version
      And an MCP client requesting protocol version "2024-11-05" connects to the installed server
    Then the server should offer a tool from each of these modules:
      | module      | tool              |
      | attachments | list_attachments  |
      | boards      | list_boards       |
      | cards       | list_cards        |
      | checklists  | list_check_items  |
      | comments    | list_comments     |
      | labels      | list_board_labels |
      | lists       | list_lists        |
      | members     | get_me            |
      | search      | search            |
      | webhooks    | list_webhooks     |

    Examples:
      | boundary         |
      | newest permitted |
      | lowest supported |

  # --- The two boundaries must actually differ (§4.3, guards §2.3) ---
  #
  # If the pin were ignored, both Examples rows above would silently
  # exercise the identical dependency set and the variance this feature
  # relies on would be gone without any signal. This scenario verifies the
  # boundaries through a second, independent channel: the installed
  # distribution metadata. It also confirms the upper bound still bites —
  # if the declared ceiling were dropped, "newest permitted" would install
  # an mcp 2.x and this scenario would say so directly, rather than
  # leaving it to be inferred from an import traceback elsewhere.

  Scenario: The two boundaries install different mcp versions
    When the installed mcp version is recorded for the newest permitted mcp version
      And the installed mcp version is recorded for the lowest supported mcp version
    Then the two recorded mcp versions should differ
      And the version recorded for the lowest supported mcp version should be the declared floor
      And the version recorded for the newest permitted mcp version should satisfy the declared upper bound
