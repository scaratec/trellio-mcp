Feature: MCP Prompts
  As an MCP client using the trello-mcp server
  I want to use predefined prompt templates
  So that I can quickly generate structured requests

  Background:
    Given a configured trello-mcp server

  # --- summarize_board ---

  Scenario Outline: Summarize board prompt
    When I get the prompt "summarize_board" with arguments:
      | board_id   |
      | <board_id> |
    Then the prompt message should contain "<board_id>"
      And the prompt message should contain "summarize"

    Examples:
      | board_id |
      | bd-100   |
      | bd-200   |

  # --- create_sprint ---

  Scenario Outline: Create sprint prompt
    When I get the prompt "create_sprint" with arguments:
      | board_id   | sprint_name   |
      | <board_id> | <sprint_name> |
    Then the prompt message should contain "<board_id>"
      And the prompt message should contain "<sprint_name>"

    Examples:
      | board_id | sprint_name |
      | bd-100   | Sprint 42   |
      | bd-200   | Sprint 43   |

  # --- daily_standup ---

  Scenario Outline: Daily standup prompt
    When I get the prompt "daily_standup" with arguments:
      | board_id   |
      | <board_id> |
    Then the prompt message should contain "<board_id>"
      And the prompt message should contain "standup"

    Examples:
      | board_id |
      | bd-100   |
      | bd-200   |
