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


@given('the Trello API will return an updated list with id "{list_id}" and name "{name}"')
def step_api_returns_updated_list(context, list_id, name):
    async def mock_update(list_id, **kwargs):
        return TrelloList(
            id=list_id, name=kwargs.get("name", name),
            idBoard="bd-000", closed=kwargs.get("closed", False),
        )
    context.mock_client.update_list.side_effect = mock_update


@given('the Trello API will return an archived list with id "{list_id}"')
def step_api_returns_archived_list(context, list_id):
    async def mock_update(list_id, **kwargs):
        return TrelloList(
            id=list_id, name="Archived", idBoard="bd-000", closed=True,
        )
    context.mock_client.update_list.side_effect = mock_update


@when('I call the "create_list" tool with:')
def step_call_create_list(context):
    from trello_mcp.tools.lists import create_list
    row = context.table[0]
    context.result = run_async(create_list(
        board_id=row["board_id"],
        name=row["name"],
    ))


@when('I call the "update_list" tool with:')
def step_call_update_list(context):
    from trello_mcp.tools.lists import update_list
    row = context.table[0]
    kwargs = {h: row[h] for h in context.table.headings}
    context.result = run_async(update_list(**kwargs))


@when('I call the "archive_list" tool with list_id "{list_id}"')
def step_call_archive_list(context, list_id):
    from trello_mcp.tools.lists import archive_list
    context.result = run_async(archive_list(list_id=list_id))
