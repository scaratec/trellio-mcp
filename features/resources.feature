Feature: MCP Resources
  As an MCP client using the trello-mcp server
  I want to read Trello data as MCP resources
  So that I can load board and card context into conversations

  Background:
    Given a configured trello-mcp server

  # --- trello://board/{board_id} ---

  Scenario Outline: Read board resource
    Given the Trello API returns board "<board_id>" with name "<board_name>"
      And the Trello API returns lists for board "<board_id>":
        | id     | name  |
        | ls-001 | To Do |
      And the Trello API returns cards for list "ls-001":
        | id     | name       | desc   |
        | cd-001 | Task Alpha | First  |
    When I read the resource "trello://board/<board_id>"
    Then the resource content should have field "board" as an object
      And in resource "board" field "name" should be "<board_name>"
      And the resource content should have field "lists" as a list with 1 entry

    Examples:
      | board_id | board_name |
      | bd-100   | Sprint Q3  |
      | bd-200   | Release v2 |

  # --- trello://card/{card_id} ---

  Scenario Outline: Read card resource
    Given the Trello API returns card "<card_id>" with name "<card_name>" and desc "<desc>"
      And the Trello API returns checklists for card "<card_id>":
        | id     | name         |
        | cl-001 | Deploy Steps |
      And the Trello API returns comments for card "<card_id>":
        | id     | text            |
        | cm-001 | Looks good      |
      And the Trello API returns attachments for card "<card_id>":
        | id     | name     | url                      |
        | at-001 | spec.pdf | https://example.com/spec |
    When I read the resource "trello://card/<card_id>"
    Then the resource content should have field "card" as an object
      And in resource "card" field "name" should be "<card_name>"
      And the resource content should have field "checklists" as a list with 1 entry
      And the resource content should have field "comments" as a list with 1 entry
      And the resource content should have field "attachments" as a list with 1 entry

    Examples:
      | card_id | card_name     | desc        |
      | cd-100  | Design Review | UX feedback |
      | cd-200  | Deploy v2     | Production  |
