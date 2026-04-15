Feature: Comment Tools
  As an MCP client using the trello-mcp server
  I want to manage Trello comments via MCP tools
  So that I can communicate within cards

  Background:
    Given a configured trello-mcp server

  # --- list_comments ---

  Scenario Outline: List comments on a card
    Given the Trello API returns comments for card "<card_id>":
      | id     | text              |
      | cm-001 | Looks good to me  |
      | cm-002 | Needs more tests  |
    When I call the "list_comments" tool with card_id "<card_id>"
    Then the result should be a JSON list with 2 entries
      And entry 0 should have field "id" with value "cm-001"
      And entry 0 should have field "text" with value "Looks good to me"
      And entry 1 should have field "id" with value "cm-002"
      And entry 1 should have field "text" with value "Needs more tests"

    Examples:
      | card_id |
      | cd-100  |
      | cd-200  |

  # --- add_comment ---

  Scenario Outline: Add a comment to a card
    Given the Trello API will return a created comment with id "<cm_id>"
    When I call the "add_comment" tool with:
      | card_id   | text   |
      | <card_id> | <text> |
    Then the result should have field "id" with value "<cm_id>"
      And the result should have field "text" with value "<text>"
      And the Trello client "add_comment" should have been called with:
        | argument | value     |
        | card_id  | <card_id> |
        | text     | <text>    |

    Examples:
      | card_id | text             | cm_id  |
      | cd-100  | LGTM             | cm-101 |
      | cd-200  | Please rework    | cm-202 |

  # --- update_comment ---

  Scenario Outline: Update a comment
    Given the Trello API will return an updated comment with id "<cm_id>" and text "<new_text>"
    When I call the "update_comment" tool with:
      | comment_id | text       |
      | <cm_id>    | <new_text> |
    Then the result should have field "id" with value "<cm_id>"
      And the result should have field "text" with value "<new_text>"
      And the Trello client "update_comment" should have been called with:
        | argument   | value      |
        | comment_id | <cm_id>    |
        | text       | <new_text> |

    Examples:
      | cm_id  | new_text         |
      | cm-301 | Updated feedback |
      | cm-302 | Revised comment  |

  # --- delete_comment ---

  Scenario Outline: Delete a comment
    Given the Trello API will accept comment deletion
    When I call the "delete_comment" tool with comment_id "<cm_id>"
    Then the result should confirm deletion
      And the Trello client "delete_comment" should have been called with:
        | argument   | value  |
        | comment_id | <cm_id>|

    Examples:
      | cm_id  |
      | cm-401 |
      | cm-402 |

  # --- Archived card validation ---

  Scenario: Reject adding a comment to an archived card
    Given the card "cd-archived" is archived with name "Old Task"
    When I attempt to call "add_comment" with:
      | card_id     | text         |
      | cd-archived | Ghost note   |
    Then the tool should raise an error
      And the error message should contain "archived"
