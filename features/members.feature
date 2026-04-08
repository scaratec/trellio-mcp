Feature: Member Tools
  As an MCP client using the trello-mcp server
  I want to query Trello members via MCP tools
  So that I can identify who is working on what

  Background:
    Given a configured trello-mcp server

  # --- get_me ---

  Scenario: Get authenticated user
    Given the Trello API returns me with id "mb-001" username "alice" and full_name "Alice Smith"
    When I call the "get_me" tool
    Then the result should have field "id" with value "mb-001"
      And the result should have field "username" with value "alice"
      And the result should have field "fullName" with value "Alice Smith"

  # --- list_board_members ---

  Scenario Outline: List members on a board
    Given the Trello API returns members for board "<board_id>":
      | id     | username | full_name   |
      | mb-001 | alice    | Alice Smith |
      | mb-002 | bob      | Bob Jones   |
    When I call the "list_board_members" tool with board_id "<board_id>"
    Then the result should be a JSON list with 2 entries
      And entry 0 should have field "username" with value "alice"
      And entry 1 should have field "username" with value "bob"

    Examples:
      | board_id |
      | bd-100   |
      | bd-200   |

  # --- get_member ---

  Scenario Outline: Get a member by ID
    Given the Trello API returns member "<member_id>" with username "<username>" and full_name "<full_name>"
    When I call the "get_member" tool with member_id "<member_id>"
    Then the result should have field "id" with value "<member_id>"
      And the result should have field "username" with value "<username>"
      And the result should have field "fullName" with value "<full_name>"

    Examples:
      | member_id | username | full_name   |
      | mb-301    | charlie  | Charlie Day |
      | mb-302    | diana    | Diana Ross  |
