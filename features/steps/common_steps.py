import asyncio
import json

from behave import given, then
from mcp.server.fastmcp.exceptions import ToolError


def run_async(coro):
    return asyncio.run(coro)


def capture_tool_error(context, coro):
    try:
        context.result = run_async(coro)
        context.error = None
    except ToolError as e:
        context.error = e
        context.result = None


@given('a configured trello-mcp server')
def step_configured_server(context):
    # Mock client is already injected via environment.py
    pass


@then('the result should be a JSON list with {count:d} entries')
def step_result_is_json_list(context, count):
    data = json.loads(context.result)
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert len(data) == count, f"Expected {count} entries, got {len(data)}"
    context.result_data = data


@then('entry {index:d} should have field "{field}" with value "{value}"')
def step_entry_has_field(context, index, field, value):
    data = context.result_data
    assert index < len(data), f"Index {index} out of range (len={len(data)})"
    actual = str(data[index][field])
    assert actual == value, f"Expected {field}={value}, got {actual}"


@then('the result should have field "{field}" with value "{value}"')
def step_result_has_field(context, field, value):
    data = json.loads(context.result)
    actual = str(data[field])
    assert actual == value, f"Expected {field}={value}, got {actual}"


@then('the result should confirm deletion')
def step_result_confirms_deletion(context):
    data = json.loads(context.result)
    assert data.get("deleted") is True, f"Expected deleted=true, got {data}"


@then('the Trello client "{method}" should have been called with:')
def step_client_called_with(context, method):
    mock_method = getattr(context.mock_client, method)
    assert mock_method.called, f"{method} was not called"
    _, kwargs = mock_method.call_args
    for row in context.table:
        arg_name = row["argument"]
        expected = row["value"]
        actual = str(kwargs.get(arg_name, ""))
        assert actual == expected, (
            f"{method}({arg_name}): expected {expected}, got {actual}"
        )
