Feature: Board Overview Composite Tool
  As an MCP client using the trello-mcp server
  I want to get a complete board overview in a single tool call
  So that I can see the board structure without multiple requests

  Background:
    Given a configured trello-mcp server

  # The only composite tool: aggregates get_board + list_lists + list_cards
  # Anti-hardcoding: 2 board variants (§2.3)

  Scenario Outline: Get board overview with lists and cards
    Given the Trello API returns board "<board_id>" with name "<board_name>"
      And the Trello API returns lists for board "<board_id>":
        | id      | name   |
        | ls-001  | To Do  |
        | ls-002  | Done   |
      And the Trello API returns cards for list "ls-001":
        | id     | name       | desc   |
        | cd-001 | Task Alpha | First  |
      And the Trello API returns cards for list "ls-002":
        | id     | name      | desc   |
        | cd-002 | Task Beta | Second |
    When I call the "get_board_overview" tool with board_id "<board_id>"
    Then the result should have field "board" as an object
      And in "board" field "id" should be "<board_id>"
      And in "board" field "name" should be "<board_name>"
      And the result should have field "lists" as a list with 2 entries
      And in "lists" entry 0 field "name" should be "To Do"
      And in "lists" entry 0 field "cards" should be a list with 1 entry
      And in "lists" entry 1 field "name" should be "Done"
      And in "lists" entry 1 field "cards" should be a list with 1 entry

    Examples:
      | board_id | board_name     |
      | bd-100   | Sprint Q3      |
      | bd-200   | Release v2     |

  Scenario: Board overview with empty lists
    Given the Trello API returns board "bd-300" with name "Empty Board"
      And the Trello API returns lists for board "bd-300":
        | id | name |
    When I call the "get_board_overview" tool with board_id "bd-300"
    Then the result should have field "lists" as a list with 0 entries
