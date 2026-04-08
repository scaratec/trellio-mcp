import json
import os
import stat
import tempfile
from unittest.mock import patch
from urllib.parse import urlparse, parse_qs

from behave import given, when, then


@given('stored credentials with api_key "{api_key}" and token "{token}"')
def step_stored_credentials(context, api_key, token):
    context._tmp_dir = tempfile.mkdtemp()
    context._cred_path = os.path.join(context._tmp_dir, "credentials.json")
    os.makedirs(context._tmp_dir, mode=0o700, exist_ok=True)
    with open(context._cred_path, "w") as f:
        json.dump({"api_key": api_key, "token": token}, f)
    os.chmod(context._cred_path, 0o600)


@given('no stored credentials exist')
def step_no_stored_credentials(context):
    context._tmp_dir = tempfile.mkdtemp()
    context._cred_path = os.path.join(context._tmp_dir, "credentials.json")
    # File does not exist


@given('environment variable TRELLO_API_KEY is "{value}"')
def step_env_api_key(context, value):
    context._env_api_key = value


@given('environment variable TRELLO_TOKEN is "{value}"')
def step_env_token(context, value):
    context._env_token = value


@when('the server resolves credentials')
def step_resolve_credentials(context):
    from trello_mcp.auth import load_credentials
    env = {
        "TRELLO_API_KEY": context._env_api_key,
        "TRELLO_TOKEN": context._env_token,
    }
    with patch("trello_mcp.auth._credentials_path", return_value=context._cred_path):
        stored = load_credentials()
    if stored:
        context._resolved_key, context._resolved_token = stored
    else:
        context._resolved_key = env["TRELLO_API_KEY"]
        context._resolved_token = env["TRELLO_TOKEN"]


@then('the resolved api_key should be "{expected}"')
def step_assert_api_key(context, expected):
    assert context._resolved_key == expected, (
        f"Expected api_key={expected}, got {context._resolved_key}"
    )


@then('the resolved token should be "{expected}"')
def step_assert_token(context, expected):
    assert context._resolved_token == expected, (
        f"Expected token={expected}, got {context._resolved_token}"
    )


@when('credentials are stored with api_key "{api_key}" and token "{token}"')
def step_store_credentials(context, api_key, token):
    context._tmp_dir = tempfile.mkdtemp()
    context._cred_path = os.path.join(context._tmp_dir, "credentials.json")
    from trello_mcp.auth import store_credentials
    with patch("trello_mcp.auth._credentials_path", return_value=context._cred_path):
        with patch("trello_mcp.auth._credentials_dir", return_value=context._tmp_dir):
            store_credentials(api_key, token)


@then('loading credentials should return api_key "{expected}"')
def step_assert_loaded_api_key(context, expected):
    from trello_mcp.auth import load_credentials
    with patch("trello_mcp.auth._credentials_path", return_value=context._cred_path):
        creds = load_credentials()
    assert creds is not None, "Expected credentials, got None"
    assert creds[0] == expected, f"Expected api_key={expected}, got {creds[0]}"


@then('loading credentials should return token "{expected}"')
def step_assert_loaded_token(context, expected):
    from trello_mcp.auth import load_credentials
    with patch("trello_mcp.auth._credentials_path", return_value=context._cred_path):
        creds = load_credentials()
    assert creds is not None, "Expected credentials, got None"
    assert creds[1] == expected, f"Expected token={expected}, got {creds[1]}"


@then('the credentials file should have permissions {mode:d}')
def step_assert_file_permissions(context, mode):
    file_stat = os.stat(context._cred_path)
    actual = stat.S_IMODE(file_stat.st_mode)
    expected = int(str(mode), 8)
    assert actual == expected, f"Expected {oct(expected)}, got {oct(actual)}"


@then('the credentials directory should have permissions {mode:d}')
def step_assert_dir_permissions(context, mode):
    dir_stat = os.stat(context._tmp_dir)
    actual = stat.S_IMODE(dir_stat.st_mode)
    expected = int(str(mode), 8)
    assert actual == expected, f"Expected {oct(expected)}, got {oct(actual)}"


# --- Auth URL ---

@given('an api_key "{api_key}"')
def step_set_api_key(context, api_key):
    context._auth_api_key = api_key


@given('a callback port {port:d}')
def step_set_port(context, port):
    context._auth_port = port


@when('the auth URL is constructed')
def step_construct_auth_url(context):
    from trello_mcp.auth import build_auth_url
    context._auth_url = build_auth_url(
        context._auth_api_key, context._auth_port,
    )


@then('the URL should start with "{prefix}"')
def step_url_starts_with(context, prefix):
    assert context._auth_url.startswith(prefix), (
        f"Expected URL to start with {prefix}, got {context._auth_url}"
    )


@then('the URL should contain parameter "{param}" with value "{value}"')
def step_url_has_param(context, param, value):
    parsed = urlparse(context._auth_url)
    params = parse_qs(parsed.query)
    actual = params.get(param, [None])[0]
    assert actual == value, (
        f"Expected {param}={value}, got {actual}"
    )


@then('the URL should contain parameter "{param}" containing "{fragment}"')
def step_url_param_contains(context, param, fragment):
    parsed = urlparse(context._auth_url)
    params = parse_qs(parsed.query)
    actual = params.get(param, [""])[0]
    assert fragment in actual, (
        f"Expected {param} to contain '{fragment}', got '{actual}'"
    )
