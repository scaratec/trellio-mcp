Feature: Error Handling
  As an MCP client using the trello-mcp server
  I want clear error messages when Trello operations fail
  So that I can understand and recover from failures

  Background:
    Given a configured trello-mcp server

  # Layer-by-layer failure path enumeration (BDD Guidelines §4.5):
  #
  # | Layer                  | Count | Already covered |
  # |------------------------|-------|-----------------|
  # | Trellio client errors  | 6     | 0               |
  # | Timeout                | 1     | 0               |
  # | Composite tool errors  | 2     | 0               |
  # | Resource errors        | 2     | 0               |
  # | Total                  | 11    | 0               |
  # | New scenarios          | 11    |                 |
  #
  # Note: Input validation (missing env vars, params) is handled
  # by FastMCP framework and trellio constructor. Not retested here.

  # --- Trellio client errors (6 paths) ---
  # Anti-hardcoding: Scenario Outline with status codes (§2.3)
  # Error messages are derived from status code (visible rule)

  Scenario Outline: Tool returns error for Trello API failure
    Given the Trello API will fail with status <status> and message "<api_message>"
    When I attempt to call the "list_boards" tool
    Then the tool should raise an error
      And the error message should contain "<expected_fragment>"

    Examples:
      | status | api_message             | expected_fragment                  |
      | 400    | Invalid board name      | Invalid input: Invalid board name  |
      | 401    | Invalid API key         | Authentication failed              |
      | 403    | Forbidden resource      | Forbidden: Forbidden resource      |
      | 404    | Board not found         | Not found                          |
      | 429    | Rate limit exceeded     | Rate limited                       |
      | 500    | Internal server error   | Trello error (500)                 |

  # --- Timeout (1 path) ---

  Scenario: Tool returns error on timeout
    Given the Trello API will timeout with message "Request timed out after 30s"
    When I attempt to call the "list_boards" tool
    Then the tool should raise an error
      And the error message should contain "Request timed out"

  # --- Composite tool partial failure (2 paths) ---

  Scenario: Board overview fails when board not found
    Given the Trello API will fail on get_board with status 404 and message "Board not found"
    When I attempt to call the "get_board_overview" tool with board_id "bd-999"
    Then the tool should raise an error
      And the error message should contain "Not found"

  Scenario: Board overview fails when list_cards fails
    Given the Trello API returns board "bd-100" with name "Test Board"
      And the Trello API returns lists for board "bd-100":
        | id     | name  |
        | ls-001 | To Do |
      And the Trello API will fail on list_cards with status 500 and message "Server error"
    When I attempt to call the "get_board_overview" tool with board_id "bd-100"
    Then the tool should raise an error
      And the error message should contain "Trello error (500)"

  # --- Resource errors (2 paths) ---

  Scenario: Board resource fails when board not found
    Given the Trello API will fail on get_board with status 404 and message "Board not found"
    When I attempt to read the resource "trello://board/bd-999"
    Then the resource read should raise an error

  Scenario: Card resource fails when card not found
    Given the Trello API will fail on get_card with status 404 and message "Card not found"
    When I attempt to read the resource "trello://card/cd-999"
    Then the resource read should raise an error
