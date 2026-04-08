from behave import given, when
from trellio.models import TrelloList
from steps.common_steps import run_async


@given('the Trello API returns lists for board "{board_id}":')
def step_api_returns_lists(context, board_id):
    lists = []
    for row in context.table:
        lists.append(TrelloList(
            id=row["id"],
            name=row["name"],
            idBoard=board_id,
        ))
    context.mock_client.list_lists.return_value = lists


@given('the Trello API will return a created list with id "{list_id}"')
def step_api_returns_created_list(context, list_id):
    async def mock_create(board_id, name, pos="top"):
        return TrelloList(id=list_id, name=name, idBoard=board_id)

    context.mock_client.create_list.side_effect = mock_create


@when('I call the "list_lists" tool with board_id "{board_id}"')
def step_call_list_lists(context, board_id):
    from trello_mcp.tools.lists import list_lists
    context.result = run_async(list_lists(board_id=board_id))


@when('I call the "create_list" tool with:')
def step_call_create_list(context):
    from trello_mcp.tools.lists import create_list
    row = context.table[0]
    context.result = run_async(create_list(
        board_id=row["board_id"],
        name=row["name"],
    ))
