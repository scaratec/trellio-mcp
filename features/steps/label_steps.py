from behave import given, when
from trellio.models import TrelloLabel
from steps.common_steps import run_async


@given('the Trello API returns labels for board "{board_id}":')
def step_api_returns_labels(context, board_id):
    labels = []
    for row in context.table:
        labels.append(TrelloLabel(
            id=row["id"], name=row["name"],
            color=row["color"], idBoard=board_id,
        ))
    context.mock_client.list_board_labels.return_value = labels


@given('the Trello API will return a created label with id "{label_id}"')
def step_api_returns_created_label(context, label_id):
    async def mock_create(name, color, board_id):
        return TrelloLabel(id=label_id, name=name, color=color, idBoard=board_id)
    context.mock_client.create_label.side_effect = mock_create


@given('the Trello API will return an updated label with id "{label_id}" name "{name}" and color "{color}"')
def step_api_returns_updated_label(context, label_id, name, color):
    async def mock_update(label_id, **kwargs):
        return TrelloLabel(
            id=label_id, name=kwargs.get("name", name),
            color=kwargs.get("color", color), idBoard="bd-000",
        )
    context.mock_client.update_label.side_effect = mock_update


@given('the Trello API will accept label deletion')
def step_api_accepts_label_deletion(context):
    context.mock_client.delete_label.return_value = None


@when('I call the "list_board_labels" tool with board_id "{board_id}"')
def step_call_list_board_labels(context, board_id):
    from trello_mcp.tools.labels import list_board_labels
    context.result = run_async(list_board_labels(board_id=board_id))


@when('I call the "create_label" tool with:')
def step_call_create_label(context):
    from trello_mcp.tools.labels import create_label
    row = context.table[0]
    context.result = run_async(create_label(
        board_id=row["board_id"], name=row["name"], color=row["color"],
    ))


@when('I call the "update_label" tool with:')
def step_call_update_label(context):
    from trello_mcp.tools.labels import update_label
    row = context.table[0]
    kwargs = {h: row[h] for h in context.table.headings}
    context.result = run_async(update_label(**kwargs))


@when('I call the "delete_label" tool with label_id "{label_id}"')
def step_call_delete_label(context, label_id):
    from trello_mcp.tools.labels import delete_label
    context.result = run_async(delete_label(label_id=label_id))
