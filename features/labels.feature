Feature: Label Tools
  As an MCP client using the trello-mcp server
  I want to manage Trello labels via MCP tools
  So that I can categorize cards on boards

  Background:
    Given a configured trello-mcp server

  # --- list_board_labels ---

  Scenario Outline: List labels on a board
    Given the Trello API returns labels for board "<board_id>":
      | id     | name     | color  |
      | lb-001 | Urgent   | red    |
      | lb-002 | Feature  | green  |
    When I call the "list_board_labels" tool with board_id "<board_id>"
    Then the result should be a JSON list with 2 entries
      And entry 0 should have field "name" with value "Urgent"
      And entry 0 should have field "color" with value "red"
      And entry 1 should have field "name" with value "Feature"
      And entry 1 should have field "color" with value "green"

    Examples:
      | board_id |
      | bd-100   |
      | bd-200   |

  # --- create_label ---

  Scenario Outline: Create a label
    Given the Trello API will return a created label with id "<label_id>"
    When I call the "create_label" tool with:
      | board_id   | name   | color   |
      | <board_id> | <name> | <color> |
    Then the result should have field "id" with value "<label_id>"
      And the result should have field "name" with value "<name>"
      And the result should have field "color" with value "<color>"
      And the Trello client "create_label" should have been called with:
        | argument | value      |
        | name     | <name>     |
        | color    | <color>    |
        | board_id | <board_id> |

    Examples:
      | board_id | name    | color  | label_id |
      | bd-100   | Bug     | red    | lb-101   |
      | bd-200   | Feature | blue   | lb-202   |

  # --- update_label ---

  Scenario Outline: Update a label
    Given the Trello API will return an updated label with id "<label_id>" name "<new_name>" and color "<new_color>"
    When I call the "update_label" tool with:
      | label_id   | name       | color       |
      | <label_id> | <new_name> | <new_color> |
    Then the result should have field "id" with value "<label_id>"
      And the result should have field "name" with value "<new_name>"
      And the Trello client "update_label" should have been called with:
        | argument | value       |
        | label_id | <label_id>  |
        | name     | <new_name>  |

    Examples:
      | label_id | new_name  | new_color |
      | lb-301   | Critical  | orange    |
      | lb-302   | Backlog   | yellow    |

  # --- delete_label ---

  Scenario Outline: Delete a label
    Given the Trello API will accept label deletion
    When I call the "delete_label" tool with label_id "<label_id>"
    Then the result should confirm deletion
      And the Trello client "delete_label" should have been called with:
        | argument | value      |
        | label_id | <label_id> |

    Examples:
      | label_id |
      | lb-401   |
      | lb-402   |

  # --- Archived board validation ---

  Scenario: Reject label creation on an archived board
    Given the board "bd-archived" is archived with name "Old Project"
    When I attempt to call "create_label" with:
      | board_id    | name      | color |
      | bd-archived | Ghost Tag | red   |
    Then the tool should raise an error
      And the error message should contain "archived"
