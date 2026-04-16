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
  # Persistence validation via independent channel (§4.3)
  # The create response is the system's self-report. Verification
  # must happen through list_attachments as an independent read.

  Scenario Outline: Create an attachment and verify via list_attachments
    Given a card "<card_id>" has no attachments
    When I call the "create_attachment" tool with:
      | card_id   | url   | name   |
      | <card_id> | <url> | <name> |
    Then the result should have field "name" with value "<name>"
    When I call the "list_attachments" tool with card_id "<card_id>"
    Then the result should be a JSON list with 1 entries
      And entry 0 should have field "name" with value "<name>"
      And entry 0 should have field "url" with value "<url>"

    Examples:
      | card_id | url                     | name      |
      | cd-100  | https://example.com/doc | doc.pdf   |
      | cd-200  | https://example.com/img | image.png |

  # Anti-hardcoding (§2.3): two different attachments prove
  # that attachments accumulate rather than replace.

  Scenario: Creating two attachments on the same card persists both
    Given a card "cd-500" has no attachments
    When I call the "create_attachment" tool with:
      | card_id | url                      | name      |
      | cd-500  | https://example.com/spec | spec.pdf  |
    Then the result should have field "name" with value "spec.pdf"
    When I call the "create_attachment" tool with:
      | card_id | url                        | name       |
      | cd-500  | https://example.com/design | design.png |
    Then the result should have field "name" with value "design.png"
    When I call the "list_attachments" tool with card_id "cd-500"
    Then the result should be a JSON list with 2 entries
      And entry 0 should have field "name" with value "spec.pdf"
      And entry 1 should have field "name" with value "design.png"

  # --- get_attachment ---
  # Anti-hardcoding (§2.3): Two different attachments prove
  # that get returns the correct individual metadata.

  Scenario Outline: Get a single attachment by ID
    Given the Trello API returns attachment "<att_id>" for card "<card_id>":
      | id       | name   | url   |
      | <att_id> | <name> | <url> |
    When I call the "get_attachment" tool with card_id "<card_id>" and attachment_id "<att_id>"
    Then the result should have field "name" with value "<name>"
      And the result should have field "url" with value "<url>"

    Examples:
      | card_id | att_id | name       | url                        |
      | cd-100  | at-501 | spec.pdf   | https://example.com/spec   |
      | cd-200  | at-502 | design.png | https://example.com/design |

  # --- delete_attachment ---
  # Persistence validation via independent channel (§4.3)
  # Verify the attachment is actually gone after deletion.

  Scenario Outline: Delete an attachment and verify via list_attachments
    Given a card "<card_id>" has attachments:
      | id       | name   | url   |
      | <att_id> | <name> | <url> |
    When I call the "delete_attachment" tool with:
      | card_id   | attachment_id |
      | <card_id> | <att_id>      |
    Then the result should confirm deletion
    When I call the "list_attachments" tool with card_id "<card_id>"
    Then the result should be a JSON list with 0 entries

    Examples:
      | card_id | att_id | name      | url                     |
      | cd-100  | at-301 | old.pdf   | https://example.com/old |
      | cd-200  | at-302 | stale.png | https://example.com/x   |

  # --- Archived card validation ---

  Scenario: Reject attachment creation on an archived card
    Given the card "cd-archived" is archived with name "Old Task"
    When I attempt to call "create_attachment" with:
      | card_id     | url                      | name      |
      | cd-archived | https://example.com/gone | ghost.pdf |
    Then the tool should raise an error
      And the error message should contain "archived"
