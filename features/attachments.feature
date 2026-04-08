Feature: Attachment Tools
  As an MCP client using the trello-mcp server
  I want to manage Trello attachments via MCP tools
  So that I can link files to cards

  Background:
    Given a configured trello-mcp server

  # --- list_attachments ---

  Scenario Outline: List attachments on a card
    Given the Trello API returns attachments for card "<card_id>":
      | id     | name       | url                         |
      | at-001 | spec.pdf   | https://example.com/spec    |
      | at-002 | design.png | https://example.com/design  |
    When I call the "list_attachments" tool with card_id "<card_id>"
    Then the result should be a JSON list with 2 entries
      And entry 0 should have field "name" with value "spec.pdf"
      And entry 0 should have field "url" with value "https://example.com/spec"
      And entry 1 should have field "name" with value "design.png"

    Examples:
      | card_id |
      | cd-100  |
      | cd-200  |

  # --- create_attachment ---

  Scenario Outline: Create an attachment on a card
    Given the Trello API will return a created attachment with id "<att_id>"
    When I call the "create_attachment" tool with:
      | card_id   | url   | name   |
      | <card_id> | <url> | <name> |
    Then the result should have field "id" with value "<att_id>"
      And the result should have field "name" with value "<name>"
      And the result should have field "url" with value "<url>"
      And the Trello client "create_attachment" should have been called with:
        | argument | value     |
        | card_id  | <card_id> |
        | url      | <url>     |
        | name     | <name>    |

    Examples:
      | card_id | url                        | name      | att_id |
      | cd-100  | https://example.com/doc    | doc.pdf   | at-101 |
      | cd-200  | https://example.com/img    | image.png | at-202 |

  # --- delete_attachment ---

  Scenario Outline: Delete an attachment
    Given the Trello API will accept attachment deletion
    When I call the "delete_attachment" tool with:
      | card_id   | attachment_id |
      | <card_id> | <att_id>      |
    Then the result should confirm deletion
      And the Trello client "delete_attachment" should have been called with:
        | argument      | value     |
        | card_id       | <card_id> |
        | attachment_id | <att_id>  |

    Examples:
      | card_id | att_id |
      | cd-100  | at-301 |
      | cd-200  | at-302 |
