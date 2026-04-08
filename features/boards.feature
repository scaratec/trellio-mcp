Feature: Board Tools
  As an MCP client using the trello-mcp server
  I want to manage Trello boards via MCP tools
  So that I can organize project work in Trello

  Background:
    Given a configured trello-mcp server

  # --- list_boards ---

  Scenario: List boards returns all boards from Trello
    Given the Trello API returns boards:
      | id      | name             | closed |
      | bd-001  | Sprint Backlog   | false  |
      | bd-002  | Release Planning | false  |
    When I call the "list_boards" tool
    Then the result should be a JSON list with 2 entries
      And entry 0 should have field "id" with value "bd-001"
      And entry 0 should have field "name" with value "Sprint Backlog"
      And entry 1 should have field "id" with value "bd-002"
      And entry 1 should have field "name" with value "Release Planning"

  Scenario: List boards returns empty list when no boards exist
    Given the Trello API returns boards:
      | id | name | closed |
    When I call the "list_boards" tool
    Then the result should be a JSON list with 0 entries

  # --- create_board ---
  # Anti-hardcoding: Scenario Outline with 2 variants (§2.3)
  # Persistence validation: verify client received correct args (§4.3)

  Scenario Outline: Create a board
    Given the Trello API will return a created board with id "<board_id>"
    When I call the "create_board" tool with:
      | name   | description   |
      | <name> | <description> |
    Then the result should have field "id" with value "<board_id>"
      And the result should have field "name" with value "<name>"
      And the Trello client "create_board" should have been called with:
        | argument    | value         |
        | name        | <name>        |
        | description | <description> |

    Examples:
      | name             | description          | board_id |
      | Sprint Backlog   | Q3 sprint work       | bd-101   |
      | Release Planning | Release v2.0 tracker | bd-202   |

  Scenario: Create a board without description
    Given the Trello API will return a created board with id "bd-303"
    When I call the "create_board" tool with:
      | name        |
      | Quick Board |
    Then the result should have field "id" with value "bd-303"
      And the result should have field "name" with value "Quick Board"
      And the Trello client "create_board" should have been called with:
        | argument | value       |
        | name     | Quick Board |

  # --- get_board ---

  Scenario Outline: Get a board by ID
    Given the Trello API returns board "<board_id>" with name "<name>"
    When I call the "get_board" tool with board_id "<board_id>"
    Then the result should have field "id" with value "<board_id>"
      And the result should have field "name" with value "<name>"

    Examples:
      | board_id | name           |
      | bd-401   | Design Review  |
      | bd-402   | Bug Triage     |

  # --- update_board ---
  # Persistence validation: verify client received correct args (§4.3)

  Scenario Outline: Update a board name
    Given the Trello API will return an updated board with id "<board_id>" and name "<new_name>"
    When I call the "update_board" tool with:
      | board_id   | name       |
      | <board_id> | <new_name> |
    Then the result should have field "id" with value "<board_id>"
      And the result should have field "name" with value "<new_name>"
      And the Trello client "update_board" should have been called with:
        | argument | value      |
        | board_id | <board_id> |
        | name     | <new_name> |

    Examples:
      | board_id | new_name          |
      | bd-501   | Renamed Board     |
      | bd-502   | Updated Backlog   |

  # --- delete_board ---
  # Persistence validation: verify client received correct args (§4.3)

  Scenario Outline: Delete a board
    Given the Trello API will accept board deletion
    When I call the "delete_board" tool with board_id "<board_id>"
    Then the result should confirm deletion
      And the Trello client "delete_board" should have been called with:
        | argument | value      |
        | board_id | <board_id> |

    Examples:
      | board_id |
      | bd-601   |
      | bd-602   |
