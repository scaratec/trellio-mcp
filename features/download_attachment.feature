Feature: Download Attachment Tool
  As an MCP client using the trello-mcp server
  I want to download Trello card attachments to local files via MCP tools
  So that I can access attached documents offline

  Background:
    Given a configured trello-mcp server

  # --- Happy Path: Download with persistence validation ---
  #
  # Persistence validation (§4.3): the tool response is the system's
  # self-report, so the file on disk is checked as an independent channel.
  # The byte count is not enough on its own - a tool that writes the right
  # number of zero bytes, or writes the previous download again, reports the
  # same size. The content has to match what the attachment actually holds.
  #
  # Anti-hardcoding (§2.3): two attachments with different names and sizes
  # prove the tool generalises.

  Scenario Outline: Download an attachment and verify the local file
    Given a card "<card_id>" has a downloadable attachment "<att_id>" with name "<name>" and <size_bytes> bytes
    And a temporary download target "<target>"
    When I call the "download_attachment" tool with:
      | card_id   | attachment_id | target_path |
      | <card_id> | <att_id>      | <target>    |
    Then the result should have field "name" with value "<name>"
    And the downloaded file "<target>" should exist with <size_bytes> bytes
    And the downloaded file "<target>" should hold the content of attachment "<att_id>"

    Examples:
      | card_id | att_id | name             | size_bytes | target          |
      | cd-100  | at-601 | Quarterly Report | 2048       | dl_report.pdf   |
      | cd-200  | at-602 | Site Photo       | 4096       | dl_photo.jpg    |

  # --- The tool is a pass-through, and has to be one ---
  #
  # This server owns no download logic; it hands card and attachment on to the
  # library and gets bytes back. What can break at this layer is therefore not
  # the transfer but the handover: a swapped argument order, an identifier
  # taken from the wrong field, a card ID quietly defaulted. None of that is
  # visible in the happy path above, because there the tool could fetch any
  # attachment of the card and still satisfy every assertion.

  Scenario: Pass the requested card and attachment through unchanged
    Given a card "cd-300" has a downloadable attachment "at-701" with name "Contract" and 800 bytes
    And the same card "cd-300" has a downloadable attachment "at-702" with name "Appendix" and 800 bytes
    And a temporary download target "dl_appendix.pdf"
    When I call the "download_attachment" tool with:
      | card_id | attachment_id | target_path      |
      | cd-300  | at-702        | dl_appendix.pdf  |
    Then the library should have been asked for attachment "at-702" on card "cd-300"
    And the result should have field "name" with value "Appendix"
    And the downloaded file "dl_appendix.pdf" should hold the content of attachment "at-702"

  # --- Error Paths ---
  #
  # An MCP client sees only the error text, so the text is the interface and
  # is asserted as such. Each scenario also states what is left behind: an
  # error message alone does not say that the refusal was clean, and a tool
  # that creates or truncates the target before noticing the problem reports
  # exactly the same failure while destroying the caller's file.

  Scenario: Reject download when target path is a directory
    Given a temporary directory "not-a-file"
    When I attempt to call "download_attachment" with directory target:
      | card_id | attachment_id | target_path |
      | cd-100  | at-601        | not-a-file  |
    Then the tool should raise an error
    And the error message should contain "is a directory"
    And the directory "not-a-file" should still be empty

  Scenario: Reject download when target directory does not exist
    When I attempt to call "download_attachment" with:
      | card_id | attachment_id | target_path                   |
      | cd-100  | at-601        | /nonexistent_trellio/file.pdf |
    Then the tool should raise an error
    And the error message should contain "does not exist"
    And nothing should exist at "/nonexistent_trellio"

  Scenario: Reject download for non-existent attachment
    Given the Trello API will fail on download_attachment with status 404 and message "attachment not found"
    And a temporary download target "dl_missing.bin"
    When I attempt to call "download_attachment" with:
      | card_id | attachment_id       | target_path    |
      | cd-100  | nonexistent_att_123 | dl_missing.bin |
    Then the tool should raise an error
    And the error message should contain "Not found"
    And no file should exist at "dl_missing.bin"
