"""Steps for dependency_compatibility.feature.

These steps install the package into a throwaway environment and drive the
resulting server over stdio with raw JSON-RPC. They deliberately do not
import trello_mcp into the behave process: the whole point is to observe a
fresh installation from the outside, the way a user's MCP client does.

All dependencies resolve from PyPI. A local sibling checkout is never
injected — doing so would bypass the version constraints under test.
"""

import atexit
import json
import os
import shutil
import subprocess
import tempfile
import threading

from behave import given, when, then

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TIMEOUT_SECONDS = 360

# Built once per run and reused by every scenario.
_WHEEL_PATH = None
_WHEEL_DIR = None

# Environment allowlist. HOME is deliberately absent for two reasons:
# uv reads ~/.config/uv/uv.toml, which can redirect the index or override
# the resolution and would silently change what is being tested; and the
# server reads ~/.config/trellio-mcp/credentials.json, so an inherited HOME
# would hand a developer's real Trello credentials to the subprocess.
# UV_CACHE_DIR is passed explicitly because dropping HOME also drops uv's
# default cache location, which would make every scenario a cold install.
ENV_ALLOWLIST = ("PATH", "UV_CACHE_DIR", "SSL_CERT_FILE", "SSL_CERT_DIR")


def _clean_env():
    env = {k: os.environ[k] for k in ENV_ALLOWLIST if k in os.environ}
    env.setdefault("UV_CACHE_DIR", os.path.expanduser("~/.cache/uv"))
    return env


def _wheel():
    """Build the distributable wheel once, and return its path.

    Installing REPO_ROOT directly would be wrong twice over. uv caches the
    build of a local directory keyed on pyproject.toml, so a change under
    src/ is silently served from a stale wheel — a source regression would
    not be observable at all. And a directory install bypasses the sdist/
    wheel packaging step, so a file missing from the distribution would go
    unnoticed. Building the artifact and installing that exercises the same
    path a user's "pip install trellio-mcp" takes.
    """
    global _WHEEL_PATH, _WHEEL_DIR
    if _WHEEL_PATH is not None:
        return _WHEEL_PATH

    _WHEEL_DIR = tempfile.mkdtemp(prefix="trellio-mcp-bdd-wheel-")
    # Registered here rather than called from an environment.py hook: behave
    # loads step modules under their own module identity, so importing this
    # module from environment.py yields a second copy with empty globals and
    # the cleanup would silently do nothing.
    atexit.register(cleanup_wheel)
    build = subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", _WHEEL_DIR],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
    )
    assert build.returncode == 0, f"Building the wheel failed:\n{build.stderr[-2000:]}"

    wheels = [f for f in os.listdir(_WHEEL_DIR) if f.endswith(".whl")]
    assert len(wheels) == 1, f"Expected exactly one wheel, got {wheels}"
    _WHEEL_PATH = os.path.join(_WHEEL_DIR, wheels[0])
    return _WHEEL_PATH


def cleanup_wheel():
    """Remove the temporary wheel directory. Registered by _wheel()."""
    global _WHEEL_PATH, _WHEEL_DIR
    if _WHEEL_DIR and os.path.isdir(_WHEEL_DIR):
        shutil.rmtree(_WHEEL_DIR, ignore_errors=True)
    _WHEEL_PATH = _WHEEL_DIR = None


def _uv_command(bound, *command_args):
    """Install the wheel with mcp pinned to one end of the declared range.

    "--resolution lowest-direct" cannot be used to reach the floor here:
    the wheel is the only direct dependency, so mcp counts as transitive
    and the flag leaves it at its newest. Plain "--resolution lowest" does
    reach it, but also drags every transitive dependency to its floor,
    including a certifi old enough to be Python 2 syntax — that failure
    says nothing about this package. So the boundary is expressed as an
    explicit constraint on mcp alone, which is exactly what the scenario
    names, and everything else stays at its newest compatible version.
    """
    # --no-config: --isolated/--no-project isolate the project, not uv's own
    # configuration files. Without it an ambient uv.toml still applies.
    command = [
        "uv", "run", "--isolated", "--no-project", "--no-config",
        "--with", _wheel(),
    ]
    if bound is not None:
        command += ["--with", f"mcp=={bound}"]
    return command + list(command_args)


def _drive_server(bound, messages, expected_ids):
    """Send the messages, wait for the expected replies, then disconnect.

    stdin is held open until the replies arrive. Writing everything and
    closing stdin immediately (as subprocess.run does) races the server:
    EOF starts its shutdown, and the reply to the last request is
    sometimes lost to that shutdown rather than written out. A real MCP
    client keeps the connection open while it waits, and so does this.
    """
    process = subprocess.Popen(
        _uv_command(bound, "trellio-mcp"),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=_clean_env(),
    )

    collected, malformed = {}, []
    pending = set(expected_ids)

    def read_replies():
        for line in process.stdout:
            try:
                message = json.loads(line)
            except ValueError:
                if line.lstrip().startswith("{"):
                    malformed.append(line)
                continue  # ordinary log output
            if "id" in message:
                collected[message["id"]] = message
                pending.discard(message["id"])
                if not pending:
                    return

    reader = threading.Thread(target=read_replies, daemon=True)
    reader.start()
    try:
        process.stdin.write(_rpc(messages))
        process.stdin.flush()
    except BrokenPipeError:
        pass  # server died on startup; the assertions report why
    reader.join(TIMEOUT_SECONDS)

    # Replies are in (or the wait timed out). Now signal shutdown.
    try:
        process.stdin.close()
    except BrokenPipeError:
        pass
    try:
        returncode = process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        process.kill()
        returncode = process.wait(timeout=30)
    stderr = process.stderr.read()
    process.stderr.close()
    process.stdout.close()

    return returncode, collected, malformed, stderr


def _uv_run(bound, *command_args):
    return subprocess.run(
        _uv_command(bound, *command_args),
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
        env=_clean_env(),
    )


def _rpc(messages):
    return "".join(json.dumps(m) + "\n" for m in messages)


def _major(version):
    return int(version.split(".")[0])


def _bound_for(context, boundary):
    """Translate the boundary named in the scenario into an mcp pin.

    "newest permitted" is deliberately not a literal: it is whatever the
    declared constraints currently allow, which changes as mcp releases.
    """
    if boundary == "newest permitted":
        return None
    if boundary == "lowest supported":
        return context.declared_mcp_floor
    raise ValueError(f"Unknown mcp boundary: {boundary!r}")


def _diagnostics(context):
    report = (
        f"mcp boundary='{context.mcp_boundary}' "
        f"returncode={context.server_returncode}\n"
        f"stderr:\n{context.server_stderr[-2000:]}"
    )
    if context.malformed_output:
        report += "\nmalformed stdout lines:\n" + "\n".join(context.malformed_output[:5])
    return report


@given('the trellio-mcp package built as a distributable wheel')
def step_package_under_test(context):
    context.package_path = _wheel()
    context.recorded_versions = {}


@given('the package declares a lowest supported mcp version of "{version}"')
def step_declared_floor(context, version):
    context.declared_mcp_floor = version


@given('the package declares an mcp upper bound of "{version}"')
def step_declared_ceiling(context, version):
    context.declared_mcp_ceiling = version


@given('the server has no Trello credentials available')
def step_no_credentials(context):
    # Enforced by ENV_ALLOWLIST: neither the credential environment
    # variables nor HOME (and thus the credentials file) are passed on.
    # Asserted here so the precondition fails loudly if the allowlist grows.
    leaking = [k for k in ("TRELLO_API_KEY", "TRELLO_TOKEN", "HOME") if k in _clean_env()]
    assert not leaking, f"Credential sources leak into the server subprocess: {leaking}"


@when('the package is installed with the {boundary} mcp version')
def step_install_with_boundary(context, boundary):
    context.mcp_boundary = boundary


@when('an MCP client requesting protocol version "{protocol_version}" connects to the installed server')
def step_start_server(context, protocol_version):
    handshake = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": protocol_version,
                "capabilities": {},
                "clientInfo": {"name": "bdd-dependency-check", "version": "1"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    ]
    # The server is launched via "trellio-mcp", the console script from
    # [project.scripts] — the same entry point uvx invokes, so entry-point
    # metadata is exercised.
    (
        context.server_returncode,
        context.server_responses,
        context.malformed_output,
        context.server_stderr,
    ) = _drive_server(
        _bound_for(context, context.mcp_boundary), handshake, expected_ids=(1, 2)
    )


@when('the installed mcp version is recorded for the {boundary} mcp version')
def step_record_version(context, boundary):
    context.mcp_boundary = boundary
    run = _uv_run(
        _bound_for(context, boundary),
        "python", "-c",
        "import importlib.metadata as m; print(m.version('mcp'))",
    )
    assert run.returncode == 0, f"Version probe failed for '{boundary}':\n{run.stderr[-2000:]}"
    context.recorded_versions[boundary] = run.stdout.strip()


@then('the server should complete the MCP initialize handshake')
def step_handshake_completed(context):
    response = context.server_responses.get(1)
    assert response is not None, f"No initialize response. {_diagnostics(context)}"
    assert "result" in response, f"initialize returned an error: {response}"
    context.init_result = response["result"]


@then('the server should confirm MCP protocol version "{expected_version}"')
def step_protocol_version(context, expected_version):
    actual = context.init_result["protocolVersion"]
    assert actual == expected_version, (
        f"Expected protocol version {expected_version}, got {actual}"
    )


@then('the server process should exit cleanly')
def step_exits_cleanly(context):
    assert context.server_returncode == 0, (
        f"Server exited with a non-zero status. {_diagnostics(context)}"
    )


@then('the server should offer a tool from each of these modules:')
def step_offers_tool_per_module(context):
    response = context.server_responses.get(2)
    assert response is not None, f"No tools/list response. {_diagnostics(context)}"
    assert "result" in response, f"tools/list returned an error: {response}"
    offered = {tool["name"] for tool in response["result"]["tools"]}

    missing = [
        (row["module"], row["tool"])
        for row in context.table
        if row["tool"] not in offered
    ]
    assert not missing, (
        f"Registration modules missing from the tool registry with the "
        f"{context.mcp_boundary} mcp version: "
        + ", ".join(f"{module} (expected '{tool}')" for module, tool in missing)
        + f"\nOffered: {sorted(offered)}"
    )


@then('the two recorded mcp versions should differ')
def step_versions_differ(context):
    versions = context.recorded_versions
    assert len(set(versions.values())) > 1, (
        f"Both boundaries installed the same mcp version: {versions}. "
        f"The pin is not taking effect, so the scenarios above are not "
        f"testing distinct dependency sets."
    )


@then('the version recorded for the lowest supported mcp version should be the declared floor')
def step_version_matches_floor(context):
    actual = context.recorded_versions["lowest supported"]
    expected = context.declared_mcp_floor
    assert actual == expected, (
        f"Expected the floor {expected} to be installed, got {actual}"
    )


@then('the version recorded for the newest permitted mcp version should satisfy the declared upper bound')
def step_version_within_upper_bound(context):
    actual = context.recorded_versions["newest permitted"]
    ceiling = context.declared_mcp_ceiling
    assert _major(actual) < _major(ceiling), (
        f"Newest permitted mcp is {actual}, which is not below the declared "
        f"upper bound {ceiling}. Either the constraint in pyproject.toml no "
        f"longer holds, or this scenario's expectation is stale."
    )
