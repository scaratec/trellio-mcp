import json

from behave import when, then
from steps.common_steps import run_async


@when('I read the resource "{uri}"')
def step_read_resource(context, uri):
    from trello_mcp.resources import read_board_resource, read_card_resource
    if uri.startswith("trello://board/"):
        board_id = uri.split("/")[-1]
        context.resource_result = run_async(read_board_resource(board_id))
    elif uri.startswith("trello://card/"):
        card_id = uri.split("/")[-1]
        context.resource_result = run_async(read_card_resource(card_id))
    else:
        raise ValueError(f"Unknown resource URI: {uri}")


@then('the resource content should have field "{field}" as an object')
def step_resource_field_object(context, field):
    data = json.loads(context.resource_result)
    assert isinstance(data[field], dict), f"Expected dict, got {type(data[field])}"


@then('in resource "{field}" field "{subfield}" should be "{value}"')
def step_resource_nested_field(context, field, subfield, value):
    data = json.loads(context.resource_result)
    actual = str(data[field][subfield])
    assert actual == value, f"Expected {subfield}={value}, got {actual}"


@then('the resource content should have field "{field}" as a list with {count:d} entry')
def step_resource_field_list_singular(context, field, count):
    data = json.loads(context.resource_result)
    lst = data[field]
    assert isinstance(lst, list), f"Expected list, got {type(lst)}"
    assert len(lst) == count, f"Expected {count}, got {len(lst)}"
