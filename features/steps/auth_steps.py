import json
import os
import stat
import tempfile
from unittest.mock import patch
from urllib.parse import urlparse, parse_qs

from behave import given, when, then


# The credential directories below are created inside the scenario's own temp
# directory (context.temp_dir, opened and removed by features/environment.py)
# rather than directly under /tmp. A bare mkdtemp() produced a "/tmp/tmpXXXX"
# nobody could attribute to this suite afterwards, and nothing ever removed
# it: five of them were left behind per run (§6.2).
#
# None of the context attributes set here carries a leading underscore, and
# that is deliberate. Behave stores underscore names on the context object
# itself, outside the per-scenario layer, so they outlive the scenario and the
# feature. A scenario that does not set cred_path would then silently assert
# against its predecessor's path and pass without having checked anything
# (§6.1). The plain names are collected again at the scenario boundary.


@given('stored credentials with api_key "{api_key}" and token "{token}"')
def step_stored_credentials(context, api_key, token):
    # No os.makedirs(..., mode=0o700, exist_ok=True) here: mkdtemp() has
    # already created the directory, so that call would be a no-op that only
    # repeats the line it is supposed to be independent of. This Given is a
    # fixture for the loading scenarios; it asserts nothing about permissions.
    context.cred_dir = tempfile.mkdtemp(dir=context.temp_dir)
    context.cred_path = os.path.join(context.cred_dir, "credentials.json")
    with open(context.cred_path, "w") as f:
        json.dump({"api_key": api_key, "token": token}, f)
    os.chmod(context.cred_path, 0o600)


@given('no stored credentials exist')
def step_no_stored_credentials(context):
    context.cred_dir = tempfile.mkdtemp(dir=context.temp_dir)
    context.cred_path = os.path.join(context.cred_dir, "credentials.json")
    # File does not exist


@given('environment variable TRELLO_API_KEY is "{value}"')
def step_env_api_key(context, value):
    context.env_api_key = value


@given('environment variable TRELLO_TOKEN is "{value}"')
def step_env_token(context, value):
    context.env_token = value


@when('the server resolves credentials')
def step_resolve_credentials(context):
    from trello_mcp.auth import load_credentials
    env = {
        "TRELLO_API_KEY": context.env_api_key,
        "TRELLO_TOKEN": context.env_token,
    }
    with patch("trello_mcp.auth._credentials_path", return_value=context.cred_path):
        stored = load_credentials()
    if stored:
        context.resolved_key, context.resolved_token = stored
    else:
        context.resolved_key = env["TRELLO_API_KEY"]
        context.resolved_token = env["TRELLO_TOKEN"]


@then('the resolved api_key should be "{expected}"')
def step_assert_api_key(context, expected):
    assert context.resolved_key == expected, (
        f"Expected api_key={expected}, got {context.resolved_key}"
    )


@then('the resolved token should be "{expected}"')
def step_assert_token(context, expected):
    assert context.resolved_token == expected, (
        f"Expected token={expected}, got {context.resolved_token}"
    )


@when('credentials are stored with api_key "{api_key}" and token "{token}"')
def step_store_credentials(context, api_key, token):
    # The credentials directory must not exist yet when the product runs.
    # store_credentials() creates it with os.makedirs(..., mode=0o700,
    # exist_ok=True), and that mode is only applied on creation: handing the
    # product a directory that already exists makes exist_ok swallow the call
    # and leaves the permissions at whatever the fixture chose. A
    # tempfile.mkdtemp() directory is 0700 by construction, so the assertion
    # "the credentials directory should have permissions 0700" would then be
    # measuring tempfile's default and would stay green even if the product
    # wrote 0o777 - the fixture answering the question under test (§4.1).
    #
    # Naming an unborn path below context.temp_dir instead lets the product
    # create the directory itself, so the assertion measures the product.
    context.cred_dir = os.path.join(context.temp_dir, "trellio-mcp")
    assert not os.path.exists(context.cred_dir), (
        f"{context.cred_dir} already exists before the product runs; "
        f"os.makedirs(exist_ok=True) would then skip applying its mode and "
        f"the permission assertion would measure the fixture, not the product."
    )
    context.cred_path = os.path.join(context.cred_dir, "credentials.json")
    from trello_mcp.auth import store_credentials
    with patch("trello_mcp.auth._credentials_path", return_value=context.cred_path):
        with patch("trello_mcp.auth._credentials_dir", return_value=context.cred_dir):
            store_credentials(api_key, token)


@then('loading credentials should return api_key "{expected}"')
def step_assert_loaded_api_key(context, expected):
    from trello_mcp.auth import load_credentials
    with patch("trello_mcp.auth._credentials_path", return_value=context.cred_path):
        creds = load_credentials()
    assert creds is not None, "Expected credentials, got None"
    assert creds[0] == expected, f"Expected api_key={expected}, got {creds[0]}"


@then('loading credentials should return token "{expected}"')
def step_assert_loaded_token(context, expected):
    from trello_mcp.auth import load_credentials
    with patch("trello_mcp.auth._credentials_path", return_value=context.cred_path):
        creds = load_credentials()
    assert creds is not None, "Expected credentials, got None"
    assert creds[1] == expected, f"Expected token={expected}, got {creds[1]}"


@then('the credentials file should have permissions {mode:d}')
def step_assert_file_permissions(context, mode):
    file_stat = os.stat(context.cred_path)
    actual = stat.S_IMODE(file_stat.st_mode)
    expected = int(str(mode), 8)
    assert actual == expected, f"Expected {oct(expected)}, got {oct(actual)}"


@then('the credentials directory should have permissions {mode:d}')
def step_assert_dir_permissions(context, mode):
    dir_stat = os.stat(context.cred_dir)
    actual = stat.S_IMODE(dir_stat.st_mode)
    expected = int(str(mode), 8)
    assert actual == expected, f"Expected {oct(expected)}, got {oct(actual)}"


# --- Auth URL ---

@given('an api_key "{api_key}"')
def step_set_api_key(context, api_key):
    context.auth_api_key = api_key


@given('a callback port {port:d}')
def step_set_port(context, port):
    context.auth_port = port


@when('the auth URL is constructed')
def step_construct_auth_url(context):
    from trello_mcp.auth import build_auth_url
    context.auth_url = build_auth_url(
        context.auth_api_key, context.auth_port,
    )


@then('the URL should start with "{prefix}"')
def step_url_starts_with(context, prefix):
    assert context.auth_url.startswith(prefix), (
        f"Expected URL to start with {prefix}, got {context.auth_url}"
    )


@then('the URL should contain parameter "{param}" with value "{value}"')
def step_url_has_param(context, param, value):
    parsed = urlparse(context.auth_url)
    params = parse_qs(parsed.query)
    actual = params.get(param, [None])[0]
    assert actual == value, (
        f"Expected {param}={value}, got {actual}"
    )


@then('the URL should contain parameter "{param}" containing "{fragment}"')
def step_url_param_contains(context, param, fragment):
    parsed = urlparse(context.auth_url)
    params = parse_qs(parsed.query)
    actual = params.get(param, [""])[0]
    assert fragment in actual, (
        f"Expected {param} to contain '{fragment}', got '{actual}'"
    )
