Feature: Search Tool
  As an MCP client using the trello-mcp server
  I want to search Trello via MCP tools
  So that I can find boards and cards by keyword

  Background:
    Given a configured trello-mcp server

  # Anti-hardcoding: 2 search queries with different results (§2.3)

  Scenario Outline: Search for boards and cards
    Given the Trello API returns search results for query "<query>":
      | boards                          | cards                         |
      | <board_id>:<board_name>         | <card_id>:<card_name>         |
    When I call the "search" tool with query "<query>"
    Then the result should have field "boards" as a list with 1 entry
      And the result should have field "cards" as a list with 1 entry
      And in "boards" entry 0 field "id" should be "<board_id>"
      And in "boards" entry 0 field "name" should be "<board_name>"
      And in "cards" entry 0 field "id" should be "<card_id>"
      And in "cards" entry 0 field "name" should be "<card_name>"

    Examples:
      | query   | board_id | board_name | card_id | card_name     |
      | sprint  | bd-001   | Sprint Q3  | cd-001  | Sprint review |
      | release | bd-002   | Release v2 | cd-002  | Release notes |

  Scenario: Search with no results
    Given the Trello API returns empty search results
    When I call the "search" tool with query "nonexistent"
    Then the result should have field "boards" as a list with 0 entries
      And the result should have field "cards" as a list with 0 entries
