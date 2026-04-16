Feature: Download Attachment Tool
  As an MCP client using the trello-mcp server
  I want to download Trello card attachments to local files via MCP tools
  So that I can access attached documents offline

  Background:
    Given a configured trello-mcp server

  # --- Happy Path: Download with persistence validation ---
  # Persistence validation (§4.3): The tool response is the system's
  # self-report. The downloaded file's existence and size are verified
  # as an independent channel.
  # Anti-hardcoding (§2.3): Two different files with different
  # sizes prove the download generalises.

  Scenario Outline: Download an attachment and verify the local file
    Given a card "<card_id>" has a downloadable attachment "<att_id>" with name "<name>" and <size_bytes> bytes
    And a temporary download target "<target>"
    When I call the "download_attachment" tool with:
      | card_id   | attachment_id | target_path |
      | <card_id> | <att_id>      | <target>    |
    Then the result should have field "name" with value "<name>"
    And the downloaded file "<target>" should exist with <size_bytes> bytes

    Examples:
      | card_id | att_id | name             | size_bytes | target          |
      | cd-100  | at-601 | Quarterly Report | 2048       | dl_report.pdf   |
      | cd-200  | at-602 | Site Photo       | 4096       | dl_photo.jpg    |

  # --- Error Path: Target path is a directory ---

  Scenario: Reject download when target path is a directory
    Given a temporary directory "not-a-file"
    When I attempt to call "download_attachment" with directory target:
      | card_id | attachment_id | target_path |
      | cd-100  | at-601        | not-a-file  |
    Then the tool should raise an error
      And the error message should contain "is a directory"

  # --- Error Path: Target directory does not exist ---

  Scenario: Reject download when target directory does not exist
    When I attempt to call "download_attachment" with:
      | card_id | attachment_id | target_path                     |
      | cd-100  | at-601        | /nonexistent_trellio/file.pdf   |
    Then the tool should raise an error
      And the error message should contain "does not exist"

  # --- Error Path: Attachment not found ---

  Scenario: Reject download for non-existent attachment
    Given the Trello API will fail on get_attachment with status 404 and message "attachment not found"
    When I attempt to call "download_attachment" with:
      | card_id | attachment_id         | target_path     |
      | cd-100  | nonexistent_att_123   | /tmp/should_not_exist.bin |
    Then the tool should raise an error
      And the error message should contain "Not found"
