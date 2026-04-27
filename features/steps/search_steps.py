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


@given('the Trello API returns a card hit for query "{query}" with:')
def step_api_returns_card_hit(context, query):
    row = context.table[0]
    label_csv = row.get("idLabels", "") or ""
    labels = [l.strip() for l in label_csv.split(",") if l.strip()]
    card = TrelloCard(
        id=row["id"],
        name=row["name"],
        idList=row["idList"],
        desc=row.get("desc", "") or "",
        idLabels=labels,
    )
    context.mock_client.search.return_value = TrelloSearchResult(
        boards=[], cards=[card],
    )


@when('I call the "search" tool with query "{query}"')
def step_call_search(context, query):
    from trello_mcp.tools.search import search
    context.result = run_async(search(query=query))


@when('I call the "search" tool scoped to board "{board_id}" with query "{query}"')
def step_call_search_with_board(context, board_id, query):
    from trello_mcp.tools.search import search
    context.result = run_async(search(query=query, id_board=board_id))


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


@then('in "{field}" entry {index:d} field "{subfield}" should be the list "{csv}"')
def step_nested_field_list(context, field, index, subfield, csv):
    data = json.loads(context.result)
    actual = data[field][index][subfield]
    expected = [v.strip() for v in csv.split(",") if v.strip()]
    assert actual == expected, (
        f"Expected {subfield}={expected}, got {actual}"
    )
