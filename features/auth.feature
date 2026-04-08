Feature: Authentication and Credential Management
  As a user of the trello-mcp server
  I want to authenticate once and have credentials stored
  So that I can use the server on any machine without manual token setup

  # --- Credential loading priority ---
  # Stored credentials take precedence over env vars (§2.1)

  Scenario: Server uses stored credentials over env vars
    Given stored credentials with api_key "stored-key" and token "stored-token"
      And environment variable TRELLO_API_KEY is "env-key"
      And environment variable TRELLO_TOKEN is "env-token"
    When the server resolves credentials
    Then the resolved api_key should be "stored-key"
      And the resolved token should be "stored-token"

  Scenario: Server falls back to env vars when no stored credentials
    Given no stored credentials exist
      And environment variable TRELLO_API_KEY is "env-key"
      And environment variable TRELLO_TOKEN is "env-token"
    When the server resolves credentials
    Then the resolved api_key should be "env-key"
      And the resolved token should be "env-token"

  # --- Credential storage ---
  # Persistence validation: re-read after write (§4.3)
  # Anti-hardcoding: 2 credential variants (§2.3)

  Scenario Outline: Credentials are stored and loaded correctly
    When credentials are stored with api_key "<api_key>" and token "<token>"
    Then loading credentials should return api_key "<api_key>"
      And loading credentials should return token "<token>"

    Examples:
      | api_key          | token              |
      | key-abc-123      | tok-xyz-789        |
      | key-def-456      | tok-uvw-012        |

  Scenario: Stored credentials file has secure permissions
    When credentials are stored with api_key "test-key" and token "test-token"
    Then the credentials file should have permissions 0600
      And the credentials directory should have permissions 0700

  # --- Auth URL construction ---
  # Anti-hardcoding: 2 API key variants (§2.3)

  Scenario Outline: Auth URL contains correct parameters
    Given an api_key "<api_key>"
      And a callback port 8095
    When the auth URL is constructed
    Then the URL should start with "https://trello.com/1/authorize"
      And the URL should contain parameter "key" with value "<api_key>"
      And the URL should contain parameter "name" with value "trellio-mcp"
      And the URL should contain parameter "expiration" with value "never"
      And the URL should contain parameter "scope" with value "read,write"
      And the URL should contain parameter "response_type" with value "token"
      And the URL should contain parameter "return_url" containing "localhost:8095"

    Examples:
      | api_key          |
      | key-abc-123      |
      | key-def-456      |
