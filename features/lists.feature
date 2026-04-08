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

  # --- update_list ---
  # Anti-hardcoding + Persistence validation (§2.3, §4.3)

  Scenario Outline: Update a list name
    Given the Trello API will return an updated list with id "<list_id>" and name "<new_name>"
    When I call the "update_list" tool with:
      | list_id   | name       |
      | <list_id> | <new_name> |
    Then the result should have field "id" with value "<list_id>"
      And the result should have field "name" with value "<new_name>"
      And the Trello client "update_list" should have been called with:
        | argument | value      |
        | list_id  | <list_id>  |
        | name     | <new_name> |

    Examples:
      | list_id | new_name     |
      | ls-301  | Renamed List |
      | ls-302  | Done Done    |

  Scenario: Update a list position
    Given the Trello API will return an updated list with id "ls-401" and name "Moved"
    When I call the "update_list" tool with:
      | list_id | pos |
      | ls-401  | top |
    Then the Trello client "update_list" should have been called with:
      | argument | value  |
      | list_id  | ls-401 |
      | pos      | top    |

  # --- archive_list ---
  # Persistence validation (§4.3)

  Scenario Outline: Archive a list
    Given the Trello API will return an archived list with id "<list_id>"
    When I call the "archive_list" tool with list_id "<list_id>"
    Then the result should have field "id" with value "<list_id>"
      And the result should have field "closed" with value "True"
      And the Trello client "update_list" should have been called with:
        | argument | value     |
        | list_id  | <list_id> |
        | closed   | true      |

    Examples:
      | list_id |
      | ls-501  |
      | ls-502  |
