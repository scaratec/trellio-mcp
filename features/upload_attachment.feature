Feature: Upload Attachment Tool
  As an MCP client using the trello-mcp server
  I want to upload local files as Trello card attachments via MCP tools
  So that I can attach screenshots, documents, and photos without leaving the terminal

  Background:
    Given a configured trello-mcp server

  # --- Happy Path: Upload with explicit name ---
  # Persistence validation via independent channel (§4.3):
  # The create response is the system's self-report. Verification
  # must happen through list_attachments as an independent read.
  # Anti-hardcoding (§2.3): Two different files with different
  # names and sizes prove the upload generalises.

  Scenario Outline: Upload a local file and verify via list_attachments
    Given a card "<card_id>" accepts file uploads
    And a temporary file "<filename>" with <size_bytes> bytes of content
    When I call the "upload_attachment" tool with:
      | card_id   | file_path  | name           |
      | <card_id> | <filename> | <display_name> |
    Then the result should have field "name" with value "<display_name>"
    When I call the "list_attachments" tool with card_id "<card_id>"
    Then the result should be a JSON list with 1 entries
      And entry 0 should have field "name" with value "<display_name>"

    Examples:
      | card_id | filename   | size_bytes | display_name     |
      | cd-100  | report.pdf | 2048       | Quarterly Report |
      | cd-200  | photo.jpg  | 4096       | Site Photo       |

  # --- Happy Path: Upload without explicit name ---
  # When name is omitted, the original filename is used as display name.

  Scenario: Upload a file without explicit name defaults to filename
    Given a card "cd-300" accepts file uploads
    And a temporary file "evidence.png" with 1024 bytes of content
    When I call the "upload_attachment" tool with file_path only:
      | card_id | file_path    |
      | cd-300  | evidence.png |
    Then the result should have field "name" with value "evidence.png"
    When I call the "list_attachments" tool with card_id "cd-300"
    Then the result should be a JSON list with 1 entries
      And entry 0 should have field "name" with value "evidence.png"

  # --- Error Path: File does not exist ---

  Scenario: Reject upload when file does not exist
    When I attempt to call "upload_attachment" with:
      | card_id | file_path                              |
      | cd-100  | /tmp/trellio_nonexistent_abc123.pdf    |
    Then the tool should raise an error
      And the error message should contain "does not exist"

  # --- Error Path: Path is a directory ---

  Scenario: Reject upload when path is a directory
    Given a temporary directory "not-a-file"
    When I attempt to call "upload_attachment" with directory:
      | card_id | file_path  |
      | cd-100  | not-a-file |
    Then the tool should raise an error
      And the error message should contain "not a regular file"

  # --- Error Path: File not readable ---

  Scenario: Reject upload when file has no read permissions
    Given a temporary file "secret.pdf" with 512 bytes of content
    And the file "secret.pdf" has no read permissions
    When I attempt to call "upload_attachment" with unreadable file:
      | card_id | file_path  |
      | cd-100  | secret.pdf |
    Then the tool should raise an error
      And the error message should contain "not readable"

  # --- Error Path: Archived card ---

  Scenario: Reject upload on an archived card
    Given the card "cd-archived" is archived with name "Old Task"
    And a temporary file "ghost.pdf" with 512 bytes of content
    When I attempt to call "upload_attachment" with:
      | card_id     | file_path |
      | cd-archived | ghost.pdf |
    Then the tool should raise an error
      And the error message should contain "archived"
