Feature: Checklist Tools
  As an MCP client using the trello-mcp server
  I want to manage Trello checklists via MCP tools
  So that I can track subtasks within cards

  Background:
    Given a configured trello-mcp server

  # --- list_card_checklists ---

  Scenario Outline: List checklists on a card
    Given the Trello API returns checklists for card "<card_id>":
      | id     | name         |
      | cl-001 | Deploy Steps |
      | cl-002 | QA Checks    |
    When I call the "list_card_checklists" tool with card_id "<card_id>"
    Then the result should be a JSON list with 2 entries
      And entry 0 should have field "id" with value "cl-001"
      And entry 0 should have field "name" with value "Deploy Steps"
      And entry 1 should have field "id" with value "cl-002"
      And entry 1 should have field "name" with value "QA Checks"

    Examples:
      | card_id |
      | cd-100  |
      | cd-200  |

  # --- create_checklist ---

  Scenario Outline: Create a checklist on a card
    Given the Trello API will return a created checklist with id "<cl_id>"
    When I call the "create_checklist" tool with:
      | card_id   | name   |
      | <card_id> | <name> |
    Then the result should have field "id" with value "<cl_id>"
      And the result should have field "name" with value "<name>"
      And the Trello client "create_checklist" should have been called with:
        | argument | value     |
        | card_id  | <card_id> |
        | name     | <name>    |

    Examples:
      | card_id | name         | cl_id  |
      | cd-100  | Deploy Steps | cl-101 |
      | cd-200  | QA Checks    | cl-202 |

  # --- delete_checklist ---

  Scenario Outline: Delete a checklist
    Given the Trello API will accept checklist deletion
    When I call the "delete_checklist" tool with checklist_id "<cl_id>"
    Then the result should confirm deletion
      And the Trello client "delete_checklist" should have been called with:
        | argument     | value  |
        | checklist_id | <cl_id>|

    Examples:
      | cl_id  |
      | cl-301 |
      | cl-302 |

  # --- create_check_item ---

  Scenario Outline: Create a check item
    Given the Trello API will return a created check item with id "<ci_id>"
    When I call the "create_check_item" tool with:
      | checklist_id | name   |
      | <cl_id>      | <name> |
    Then the result should have field "id" with value "<ci_id>"
      And the result should have field "name" with value "<name>"
      And the Trello client "create_check_item" should have been called with:
        | argument     | value   |
        | checklist_id | <cl_id> |
        | name         | <name>  |

    Examples:
      | cl_id  | name           | ci_id  |
      | cl-100 | Run migrations | ci-101 |
      | cl-200 | Smoke test     | ci-202 |

  # --- update_check_item ---

  Scenario Outline: Update a check item state
    Given the Trello API will return an updated check item with id "<ci_id>" name "<name>" and state "<state>"
    When I call the "update_check_item" tool with:
      | card_id   | check_item_id | state   |
      | <card_id> | <ci_id>       | <state> |
    Then the result should have field "id" with value "<ci_id>"
      And the result should have field "state" with value "<state>"
      And the Trello client "update_check_item" should have been called with:
        | argument      | value     |
        | card_id       | <card_id> |
        | check_item_id | <ci_id>   |
        | state         | <state>   |

    Examples:
      | card_id | ci_id  | state      | name           |
      | cd-100  | ci-301 | complete   | Run migrations |
      | cd-200  | ci-302 | incomplete | Smoke test     |

  Scenario Outline: Update a check item name
    Given the Trello API will return an updated check item with id "<ci_id>" name "<new_name>" and state "incomplete"
    When I call the "update_check_item" tool with:
      | card_id   | check_item_id | name       |
      | <card_id> | <ci_id>       | <new_name> |
    Then the result should have field "id" with value "<ci_id>"
      And the result should have field "name" with value "<new_name>"
      And the Trello client "update_check_item" should have been called with:
        | argument      | value      |
        | card_id       | <card_id>  |
        | check_item_id | <ci_id>    |
        | name          | <new_name> |

    Examples:
      | card_id | ci_id  | new_name           |
      | cd-100  | ci-401 | Renamed migrations |
      | cd-200  | ci-402 | Renamed smoke      |

  Scenario Outline: Update a check item position
    Given the Trello API will return an updated check item with id "<ci_id>" name "Item" and state "incomplete"
    When I call the "update_check_item" tool with:
      | card_id   | check_item_id | pos   |
      | <card_id> | <ci_id>       | <pos> |
    Then the result should have field "id" with value "<ci_id>"
      And the Trello client "update_check_item" should have been called with:
        | argument      | value     |
        | card_id       | <card_id> |
        | check_item_id | <ci_id>   |
        | pos           | <pos>     |

    Examples:
      | card_id | ci_id  | pos    |
      | cd-100  | ci-501 | top    |
      | cd-200  | ci-502 | bottom |

  Scenario Outline: Create a check item with a position
    Given the Trello API will return a created check item with id "<ci_id>"
    When I call the "create_check_item" tool with:
      | checklist_id | name   | pos   |
      | <cl_id>      | <name> | <pos> |
    Then the result should have field "id" with value "<ci_id>"
      And the result should have field "name" with value "<name>"
      And the Trello client "create_check_item" should have been called with:
        | argument     | value   |
        | checklist_id | <cl_id> |
        | name         | <name>  |
        | pos          | <pos>   |

    Examples:
      | cl_id  | name        | pos    | ci_id  |
      | cl-100 | Top item    | top    | ci-601 |
      | cl-200 | Bottom item | bottom | ci-602 |

  # --- delete_check_item ---

  Scenario Outline: Delete a check item
    Given the Trello API will accept check item deletion
    When I call the "delete_check_item" tool with:
      | checklist_id | check_item_id |
      | <cl_id>      | <ci_id>       |
    Then the result should confirm deletion
      And the Trello client "delete_check_item" should have been called with:
        | argument      | value   |
        | checklist_id  | <cl_id> |
        | check_item_id | <ci_id> |

    Examples:
      | cl_id  | ci_id  |
      | cl-401 | ci-401 |
      | cl-402 | ci-402 |

  # --- Archived card validation ---

  Scenario: Reject checklist creation on an archived card
    Given the card "cd-archived" is archived with name "Old Task"
    When I attempt to call "create_checklist" with:
      | card_id     | name        |
      | cd-archived | Ghost Steps |
    Then the tool should raise an error
      And the error message should contain "archived"
