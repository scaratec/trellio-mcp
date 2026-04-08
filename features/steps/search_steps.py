import json

from behave import given, when, then
from trellio.models import TrelloBoard, TrelloCard, TrelloSearchResult
from steps.common_steps import run_async


@given('the Trello API returns search results for query "{query}":')
def step_api_returns_search_results(context, query):
    row = context.table[0]
    board_parts = row["boards"].split(":")
    card_parts = row["cards"].split(":")
    result = TrelloSearchResult(
        boards=[TrelloBoard(id=board_parts[0], name=board_parts[1])],
        cards=[TrelloCard(id=card_parts[0], name=card_parts[1], idList="ls-000")],
    )
    context.mock_client.search.return_value = result


@given('the Trello API returns empty search results')
def step_api_returns_empty_search(context):
    context.mock_client.search.return_value = TrelloSearchResult(
        boards=[], cards=[],
    )


@when('I call the "search" tool with query "{query}"')
def step_call_search(context, query):
    from trello_mcp.tools.search import search
    context.result = run_async(search(query=query))


@then('the result should have field "{field}" as a list with {count:d} entry')
def step_result_field_list_singular(context, field, count):
    data = json.loads(context.result)
    lst = data[field]
    assert isinstance(lst, list), f"Expected list, got {type(lst)}"
    assert len(lst) == count, f"Expected {count}, got {len(lst)}"


@then('the result should have field "{field}" as a list with {count:d} entries')
def step_result_field_list(context, field, count):
    data = json.loads(context.result)
    lst = data[field]
    assert isinstance(lst, list), f"Expected list, got {type(lst)}"
    assert len(lst) == count, f"Expected {count}, got {len(lst)}"


@then('in "{field}" entry {index:d} field "{subfield}" should be "{value}"')
def step_nested_field(context, field, index, subfield, value):
    data = json.loads(context.result)
    actual = str(data[field][index][subfield])
    assert actual == value, f"Expected {subfield}={value}, got {actual}"
