Feature: Card Tools
  As an MCP client using the trello-mcp server
  I want to manage Trello cards via MCP tools
  So that I can track individual work items

  Background:
    Given a configured trello-mcp server

  # --- list_cards ---

  Scenario Outline: List cards in a list
    Given the Trello API returns cards for list "<list_id>":
      | id     | name            | desc          |
      | cd-001 | Fix login bug   | Urgent fix    |
      | cd-002 | Add dark mode   | UI feature    |
    When I call the "list_cards" tool with list_id "<list_id>"
    Then the result should be a JSON list with 2 entries
      And entry 0 should have field "id" with value "cd-001"
      And entry 0 should have field "name" with value "Fix login bug"
      And entry 1 should have field "id" with value "cd-002"
      And entry 1 should have field "name" with value "Add dark mode"

    Examples:
      | list_id |
      | ls-100  |
      | ls-200  |

  Scenario: List cards in empty list
    Given the Trello API returns cards for list "ls-empty":
      | id | name | desc |
    When I call the "list_cards" tool with list_id "ls-empty"
    Then the result should be a JSON list with 0 entries

  # --- create_card ---
  # Anti-hardcoding + Persistence validation (§2.3, §4.3)

  Scenario Outline: Create a card
    Given the Trello API will return a created card with id "<card_id>"
    When I call the "create_card" tool with:
      | list_id   | name   | desc   |
      | <list_id> | <name> | <desc> |
    Then the result should have field "id" with value "<card_id>"
      And the result should have field "name" with value "<name>"
      And the Trello client "create_card" should have been called with:
        | argument | value     |
        | list_id  | <list_id> |
        | name     | <name>    |
        | desc     | <desc>    |

    Examples:
      | list_id | name          | desc           | card_id |
      | ls-100  | Fix login bug | Critical issue | cd-101  |
      | ls-200  | Add search    | New feature    | cd-202  |

  Scenario: Create a card without description
    Given the Trello API will return a created card with id "cd-303"
    When I call the "create_card" tool with:
      | list_id | name        |
      | ls-100  | Quick Task  |
    Then the result should have field "id" with value "cd-303"
      And the result should have field "name" with value "Quick Task"
      And the Trello client "create_card" should have been called with:
        | argument | value      |
        | list_id  | ls-100     |
        | name     | Quick Task |

  # --- Unicode handling ---
  # Bug fix: json.dumps escapes non-ASCII by default (§2.3)

  Scenario Outline: Create a card with Unicode characters
    Given the Trello API will return a created card with id "<card_id>"
    When I call the "create_card" tool with:
      | list_id | name   |
      | ls-100  | <name> |
    Then the raw result should contain "<raw_fragment>"

    Examples:
      | name                  | raw_fragment | card_id |
      | Zahlung (200€)        | 200€         | cd-u01  |
      | Rücksprache mit Jörg  | Rücksprache  | cd-u02  |

  # --- create_card with due date ---
  # Anti-hardcoding: 2 ISO 8601 date variants (§2.3)
  # Persistence validation (§4.3)

  Scenario Outline: Create a card with a due date
    Given the Trello API will return a created card with id "<card_id>"
    When I call the "create_card" tool with:
      | list_id   | name   | due   |
      | <list_id> | <name> | <due> |
    Then the result should have field "id" with value "<card_id>"
      And the Trello client "create_card" should have been called with:
        | argument | value     |
        | list_id  | <list_id> |
        | name     | <name>    |
        | due      | <due>     |

    Examples:
      | list_id | name          | due                  | card_id |
      | ls-100  | Sprint Review | 2026-04-15T10:00:00Z | cd-901  |
      | ls-200  | Release Day   | 2026-05-01T18:00:00Z | cd-902  |

  # --- update_card with due date and dueComplete ---

  Scenario Outline: Update a card due date and mark complete
    Given the Trello API will return an updated card with id "<card_id>" and name "Task"
    When I call the "update_card" tool with:
      | card_id   | due   | dueComplete   |
      | <card_id> | <due> | <dueComplete> |
    Then the Trello client "update_card" should have been called with:
      | argument    | value         |
      | card_id     | <card_id>     |
      | due         | <due>         |
      | dueComplete | <dueComplete> |

    Examples:
      | card_id | due                  | dueComplete |
      | cd-501  | 2026-04-20T09:00:00Z | false       |
      | cd-502  | 2026-06-01T12:00:00Z | true        |

  # --- create_card with position ---
  # Trellio supports pos parameter (§2.3 anti-hardcoding)

  Scenario Outline: Create a card at a specific position
    Given the Trello API will return a created card with id "<card_id>"
    When I call the "create_card" tool with:
      | list_id   | name   | pos   |
      | <list_id> | <name> | <pos> |
    Then the result should have field "id" with value "<card_id>"
      And the Trello client "create_card" should have been called with:
        | argument | value     |
        | list_id  | <list_id> |
        | name     | <name>    |
        | pos      | <pos>     |

    Examples:
      | list_id | name       | pos    | card_id |
      | ls-100  | Top Task   | top    | cd-701  |
      | ls-200  | Bottom Job | bottom | cd-702  |

  # --- create_card with labels ---

  Scenario: Create a card with labels
    Given the Trello API will return a created card with id "cd-801"
    When I call the "create_card" tool with:
      | list_id | name         | idLabels        |
      | ls-100  | Labeled Task | lb-001,lb-002   |
    Then the result should have field "id" with value "cd-801"
      And the Trello client "create_card" should have been called with:
        | argument | value           |
        | list_id  | ls-100          |
        | name     | Labeled Task    |
        | idLabels | lb-001,lb-002   |

  # --- update_card with position and labels ---

  Scenario: Update a card position and labels
    Given the Trello API will return an updated card with id "cd-901" and name "Moved Card"
    When I call the "update_card" tool with:
      | card_id | pos    | idLabels      |
      | cd-901  | top    | lb-003,lb-004 |
    Then the Trello client "update_card" should have been called with:
      | argument | value         |
      | card_id  | cd-901        |
      | pos      | top           |
      | idLabels | lb-003,lb-004 |

  # --- add_label_to_card ---
  # Persistence validation (§4.3)

  Scenario Outline: Add a label to a card
    Given the Trello API will accept adding a label to a card
    When I call the "add_label_to_card" tool with:
      | card_id   | label_id   |
      | <card_id> | <label_id> |
    Then the result should confirm success
      And the Trello client "add_label_to_card" should have been called with:
        | argument | value      |
        | card_id  | <card_id>  |
        | label_id | <label_id> |

    Examples:
      | card_id | label_id |
      | cd-100  | lb-001   |
      | cd-200  | lb-002   |

  # --- remove_label_from_card ---

  Scenario Outline: Remove a label from a card
    Given the Trello API will accept removing a label from a card
    When I call the "remove_label_from_card" tool with:
      | card_id   | label_id   |
      | <card_id> | <label_id> |
    Then the result should confirm success
      And the Trello client "remove_label_from_card" should have been called with:
        | argument | value      |
        | card_id  | <card_id>  |
        | label_id | <label_id> |

    Examples:
      | card_id | label_id |
      | cd-100  | lb-001   |
      | cd-200  | lb-002   |

  # --- get_card ---

  Scenario Outline: Get a card by ID
    Given the Trello API returns card "<card_id>" with name "<name>" and desc "<desc>"
    When I call the "get_card" tool with card_id "<card_id>"
    Then the result should have field "id" with value "<card_id>"
      And the result should have field "name" with value "<name>"
      And the result should have field "desc" with value "<desc>"

    Examples:
      | card_id | name          | desc        |
      | cd-401  | Design Review | UX feedback |
      | cd-402  | Deploy v2     | Production  |

  # --- get_card returns idLabels ---

  Scenario: Get a card includes assigned labels
    Given the Trello API returns card "cd-701" with name "Labeled" desc "test" and labels "lb-001,lb-002"
    When I call the "get_card" tool with card_id "cd-701"
    Then the result should have field "id" with value "cd-701"
      And the result field "idLabels" should be the list "lb-001,lb-002"

  # --- list_cards returns idLabels ---

  Scenario: List cards includes assigned labels
    Given the Trello API returns cards with labels for list "ls-100":
      | id     | name      | idLabels      |
      | cd-801 | Task One  | lb-001,lb-002 |
      | cd-802 | Task Two  | lb-003        |
    When I call the "list_cards" tool with list_id "ls-100"
    Then the result should be a JSON list with 2 entries
      And entry 0 field "idLabels" should be the list "lb-001,lb-002"
      And entry 1 field "idLabels" should be the list "lb-003"

  # --- update_card ---
  # Persistence validation (§4.3)

  Scenario Outline: Update a card
    Given the Trello API will return an updated card with id "<card_id>" and name "<new_name>"
    When I call the "update_card" tool with:
      | card_id   | name       |
      | <card_id> | <new_name> |
    Then the result should have field "id" with value "<card_id>"
      And the result should have field "name" with value "<new_name>"
      And the Trello client "update_card" should have been called with:
        | argument | value      |
        | card_id  | <card_id>  |
        | name     | <new_name> |

    Examples:
      | card_id | new_name         |
      | cd-501  | Renamed Card     |
      | cd-502  | Updated Feature  |

  # --- delete_card ---

  Scenario Outline: Delete a card
    Given the Trello API will accept card deletion
    When I call the "delete_card" tool with card_id "<card_id>"
    Then the result should confirm deletion
      And the Trello client "delete_card" should have been called with:
        | argument | value     |
        | card_id  | <card_id> |

    Examples:
      | card_id |
      | cd-601  |
      | cd-602  |
