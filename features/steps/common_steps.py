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


@then('the raw result should contain "{fragment}"')
def step_raw_result_contains(context, fragment):
    assert fragment in context.result, (
        f"Expected '{fragment}' in result, got: {context.result}"
    )


@then('the result field "{field}" should be an empty list')
def step_result_field_is_empty_list(context, field):
    data = json.loads(context.result)
    actual = data[field]
    assert actual == [], f"Expected {field}=[], got {actual}"


@then('the result field "{field}" should be the list "{csv}"')
def step_result_field_is_list(context, field, csv):
    data = json.loads(context.result)
    expected = [v.strip() for v in csv.split(",")]
    actual = data[field]
    assert actual == expected, f"Expected {field}={expected}, got {actual}"


@then('entry {index:d} field "{field}" should be the list "{csv}"')
def step_entry_field_is_list(context, index, field, csv):
    data = context.result_data
    expected = [v.strip() for v in csv.split(",")]
    actual = data[index][field]
    assert actual == expected, f"Expected {field}={expected}, got {actual}"


@then('the result should confirm success')
def step_result_confirms_success(context):
    data = json.loads(context.result)
    assert data.get("success") is True, f"Expected success=true, got {data}"


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
        raw = kwargs.get(arg_name, "")
        if isinstance(raw, bool):
            actual = str(raw).lower()
        else:
            actual = str(raw)
        assert actual == expected, (
            f"{method}({arg_name}): expected {expected}, got {actual}"
        )
