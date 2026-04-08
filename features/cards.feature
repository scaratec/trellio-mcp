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
