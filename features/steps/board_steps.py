from behave import given, when
from trellio.models import TrelloBoard
from steps.common_steps import run_async


# --- Given steps ---

@given('the Trello API returns boards:')
def step_api_returns_boards(context):
    boards = []
    for row in context.table:
        boards.append(TrelloBoard(
            id=row["id"],
            name=row["name"],
            closed=row["closed"].lower() == "true",
        ))
    context.mock_client.list_boards.return_value = boards


@given('the Trello API will return a created board with id "{board_id}"')
def step_api_returns_created_board(context, board_id):
    context._pending_board_id = board_id

    async def mock_create(name, description=None):
        return TrelloBoard(id=board_id, name=name, desc=description or "")

    context.mock_client.create_board.side_effect = mock_create


@given('the Trello API returns board "{board_id}" with name "{name}"')
def step_api_returns_board(context, board_id, name):
    async def mock_get(board_id):
        return TrelloBoard(id=board_id, name=name)

    context.mock_client.get_board.side_effect = mock_get


@given('the Trello API will return an updated board with id "{board_id}" and name "{name}"')
def step_api_returns_updated_board(context, board_id, name):
    async def mock_update(board_id, **kwargs):
        return TrelloBoard(id=board_id, name=kwargs.get("name", name))

    context.mock_client.update_board.side_effect = mock_update


@given('the Trello API will accept board deletion')
def step_api_accepts_board_deletion(context):
    context.mock_client.delete_board.return_value = None


# --- When steps ---

@when('I call the "list_boards" tool')
def step_call_list_boards(context):
    from trello_mcp.tools.boards import list_boards
    context.result = run_async(list_boards())


@when('I call the "create_board" tool with:')
def step_call_create_board(context):
    from trello_mcp.tools.boards import create_board
    row = context.table[0]
    name = row["name"]
    description = row.get("description", None)
    if description:
        context.result = run_async(create_board(name=name, description=description))
    else:
        context.result = run_async(create_board(name=name))


@when('I call the "get_board" tool with board_id "{board_id}"')
def step_call_get_board(context, board_id):
    from trello_mcp.tools.boards import get_board
    context.result = run_async(get_board(board_id=board_id))


@when('I call the "update_board" tool with:')
def step_call_update_board(context):
    from trello_mcp.tools.boards import update_board
    row = context.table[0]
    kwargs = {h: row[h] for h in context.table.headings}
    context.result = run_async(update_board(**kwargs))


@when('I call the "delete_board" tool with board_id "{board_id}"')
def step_call_delete_board(context, board_id):
    from trello_mcp.tools.boards import delete_board
    context.result = run_async(delete_board(board_id=board_id))
