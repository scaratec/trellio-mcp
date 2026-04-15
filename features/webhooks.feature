Feature: Webhook Tools
  As an MCP client using the trello-mcp server
  I want to manage Trello webhooks via MCP tools
  So that I can receive notifications about board changes

  Background:
    Given a configured trello-mcp server

  # --- list_webhooks ---

  Scenario: List all webhooks
    Given the Trello API returns webhooks:
      | id     | description    | callbackURL                  | active |
      | wh-001 | Board watcher  | https://example.com/hook1    | true   |
      | wh-002 | Card tracker   | https://example.com/hook2    | true   |
    When I call the "list_webhooks" tool
    Then the result should be a JSON list with 2 entries
      And entry 0 should have field "id" with value "wh-001"
      And entry 0 should have field "description" with value "Board watcher"
      And entry 1 should have field "id" with value "wh-002"

  # --- create_webhook ---

  Scenario Outline: Create a webhook
    Given the Trello API will return a created webhook with id "<wh_id>"
    When I call the "create_webhook" tool with:
      | callback_url   | id_model   | description   |
      | <callback_url> | <id_model> | <description> |
    Then the result should have field "id" with value "<wh_id>"
      And the result should have field "callbackURL" with value "<callback_url>"
      And the Trello client "create_webhook" should have been called with:
        | argument     | value          |
        | callback_url | <callback_url> |
        | id_model     | <id_model>     |
        | description  | <description>  |

    Examples:
      | callback_url                | id_model | description   | wh_id  |
      | https://example.com/hook1   | bd-100   | Board watcher | wh-101 |
      | https://example.com/hook2   | bd-200   | Card tracker  | wh-202 |

  # --- get_webhook ---

  Scenario Outline: Get a webhook by ID
    Given the Trello API returns webhook "<wh_id>" with description "<desc>" and callback_url "<url>"
    When I call the "get_webhook" tool with webhook_id "<wh_id>"
    Then the result should have field "id" with value "<wh_id>"
      And the result should have field "description" with value "<desc>"
      And the result should have field "callbackURL" with value "<url>"

    Examples:
      | wh_id  | desc          | url                        |
      | wh-301 | Board watcher | https://example.com/hook1  |
      | wh-302 | Card tracker  | https://example.com/hook2  |

  # --- update_webhook ---

  Scenario Outline: Update a webhook
    Given the Trello API will return an updated webhook with id "<wh_id>" and description "<new_desc>"
    When I call the "update_webhook" tool with:
      | webhook_id | description |
      | <wh_id>    | <new_desc>  |
    Then the result should have field "id" with value "<wh_id>"
      And the result should have field "description" with value "<new_desc>"
      And the Trello client "update_webhook" should have been called with:
        | argument   | value      |
        | webhook_id | <wh_id>    |
        | description| <new_desc> |

    Examples:
      | wh_id  | new_desc         |
      | wh-401 | Updated watcher  |
      | wh-402 | Revised tracker  |

  # --- delete_webhook ---

  Scenario Outline: Delete a webhook
    Given the Trello API will accept webhook deletion
    When I call the "delete_webhook" tool with webhook_id "<wh_id>"
    Then the result should confirm deletion
      And the Trello client "delete_webhook" should have been called with:
        | argument   | value  |
        | webhook_id | <wh_id>|

    Examples:
      | wh_id  |
      | wh-501 |
      | wh-502 |

  # --- Archived board validation ---

  Scenario: Reject webhook creation on an archived board
    Given the board "bd-archived" is archived with name "Old Project"
    When I attempt to call "create_webhook" with:
      | callback_url              | id_model    |
      | https://example.com/hook  | bd-archived |
    Then the tool should raise an error
      And the error message should contain "archived"
