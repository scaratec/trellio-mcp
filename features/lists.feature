Feature: List Tools
  As an MCP client using the trello-mcp server
  I want to manage Trello lists via MCP tools
  So that I can organize cards within boards

  Background:
    Given a configured trello-mcp server

  # --- list_lists ---
  # Anti-hardcoding: 2 variants (§2.3)

  Scenario Outline: List all lists on a board
    Given the Trello API returns lists for board "<board_id>":
      | id      | name       |
      | ls-001  | To Do      |
      | ls-002  | In Progress|
    When I call the "list_lists" tool with board_id "<board_id>"
    Then the result should be a JSON list with 2 entries
      And entry 0 should have field "id" with value "ls-001"
      And entry 0 should have field "name" with value "To Do"
      And entry 1 should have field "id" with value "ls-002"
      And entry 1 should have field "name" with value "In Progress"

    Examples:
      | board_id |
      | bd-100   |
      | bd-200   |

  Scenario: List lists on empty board
    Given the Trello API returns lists for board "bd-empty":
      | id | name |
    When I call the "list_lists" tool with board_id "bd-empty"
    Then the result should be a JSON list with 0 entries

  # --- create_list ---
  # Persistence validation (§4.3)

  Scenario Outline: Create a list on a board
    Given the Trello API will return a created list with id "<list_id>"
    When I call the "create_list" tool with:
      | board_id   | name   |
      | <board_id> | <name> |
    Then the result should have field "id" with value "<list_id>"
      And the result should have field "name" with value "<name>"
      And the Trello client "create_list" should have been called with:
        | argument | value      |
        | board_id | <board_id> |
        | name     | <name>     |

    Examples:
      | board_id | name        | list_id |
      | bd-100   | To Do       | ls-101  |
      | bd-200   | In Progress | ls-202  |
