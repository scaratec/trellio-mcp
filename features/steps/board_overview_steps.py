import json

from behave import when, then
from steps.common_steps import run_async


@when('I call the "get_board_overview" tool with board_id "{board_id}"')
def step_call_get_board_overview(context, board_id):
    from trello_mcp.tools.boards import get_board_overview
    context.result = run_async(get_board_overview(board_id=board_id))


@then('the result should have field "{field}" as an object')
def step_result_field_is_object(context, field):
    data = json.loads(context.result)
    assert isinstance(data[field], dict), f"Expected dict, got {type(data[field])}"
    context._overview_data = data


@then('in "{field}" field "{subfield}" should be "{value}"')
def step_overview_nested_field(context, field, subfield, value):
    data = json.loads(context.result)
    actual = str(data[field][subfield])
    assert actual == value, f"Expected {subfield}={value}, got {actual}"


@then('in "{field}" entry {index:d} field "{subfield}" should be a list with {count:d} entry')
def step_overview_nested_list_singular(context, field, index, subfield, count):
    data = json.loads(context.result)
    lst = data[field][index][subfield]
    assert isinstance(lst, list), f"Expected list, got {type(lst)}"
    assert len(lst) == count, f"Expected {count}, got {len(lst)}"
