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

  # --- Search returns extended card fields (#5) ---
  # Anti-hardcoding §2.3: 2 different cards with distinct list/desc/labels

  Scenario Outline: Search returns idList, desc and idLabels per card
    Given the Trello API returns a card hit for query "<query>" with:
      | id        | name        | idList   | desc   | idLabels   |
      | <card_id> | <card_name> | <list_id>| <desc> | <labels>   |
    When I call the "search" tool with query "<query>"
    Then in "cards" entry 0 field "id" should be "<card_id>"
      And in "cards" entry 0 field "idList" should be "<list_id>"
      And in "cards" entry 0 field "desc" should be "<desc>"
      And in "cards" entry 0 field "idLabels" should be the list "<labels>"

    Examples:
      | query   | card_id | card_name      | list_id | desc                    | labels        |
      | sprint  | cd-x01  | Sprint review  | ls-100  | Plan Q3 capacity        | lb-001,lb-002 |
      | release | cd-x02  | Release notes  | ls-200  | Cut tag and ship to PyPI| lb-003        |

  # --- Search scoped to a single board (#6) ---

  Scenario Outline: Search forwards id_board filter to the client
    Given the Trello API returns a card hit for query "<query>" with:
      | id        | name        | idList  | desc | idLabels |
      | <card_id> | <card_name> | ls-000  |      |          |
    When I call the "search" tool scoped to board "<board_id>" with query "<query>"
    Then in "cards" entry 0 field "id" should be "<card_id>"
      And the Trello client "search" should have been called with:
        | argument  | value      |
        | query     | <query>    |
        | id_boards | <board_id> |

    Examples:
      | query   | card_id | card_name     | board_id |
      | sprint  | cd-y01  | Sprint task   | bd-100   |
      | release | cd-y02  | Release task  | bd-200   |
