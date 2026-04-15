from behave import given, when
from trellio.models import TrelloBoard, TrelloCard
from steps.common_steps import capture_tool_error


@given('the board "{board_id}" is archived with name "{name}"')
def step_board_is_archived(context, board_id, name):
    async def mock_get_board(board_id=board_id, **kwargs):
        return TrelloBoard(id=board_id, name=name, closed=True)
    context.mock_client.get_board.side_effect = mock_get_board


@given('the card "{card_id}" is archived with name "{name}"')
def step_card_is_archived(context, card_id, name):
    async def mock_get_card(card_id=card_id, **kwargs):
        return TrelloCard(id=card_id, name=name, idList="ls-000", closed=True)
    context.mock_client.get_card.side_effect = mock_get_card


@when('I attempt to call "create_list" with:')
def step_attempt_create_list(context):
    from trello_mcp.tools.lists import create_list
    row = context.table[0]
    capture_tool_error(context, create_list(
        board_id=row["board_id"], name=row["name"]))


@when('I attempt to call "create_label" with:')
def step_attempt_create_label(context):
    from trello_mcp.tools.labels import create_label
    row = context.table[0]
    capture_tool_error(context, create_label(
        board_id=row["board_id"], name=row["name"], color=row["color"]))


@when('I attempt to call "create_checklist" with:')
def step_attempt_create_checklist(context):
    from trello_mcp.tools.checklists import create_checklist
    row = context.table[0]
    capture_tool_error(context, create_checklist(
        card_id=row["card_id"], name=row["name"]))


@when('I attempt to call "add_comment" with:')
def step_attempt_add_comment(context):
    from trello_mcp.tools.comments import add_comment
    row = context.table[0]
    capture_tool_error(context, add_comment(
        card_id=row["card_id"], text=row["text"]))


@when('I attempt to call "create_attachment" with:')
def step_attempt_create_attachment(context):
    from trello_mcp.tools.attachments import create_attachment
    row = context.table[0]
    capture_tool_error(context, create_attachment(
        card_id=row["card_id"], url=row["url"], name=row.get("name", "")))


@when('I attempt to call "create_webhook" with:')
def step_attempt_create_webhook(context):
    from trello_mcp.tools.webhooks import create_webhook
    row = context.table[0]
    capture_tool_error(context, create_webhook(
        callback_url=row["callback_url"], id_model=row["id_model"]))


@when('I attempt to call "add_label_to_card" with:')
def step_attempt_add_label_to_card(context):
    from trello_mcp.tools.cards import add_label_to_card
    row = context.table[0]
    capture_tool_error(context, add_label_to_card(
        card_id=row["card_id"], label_id=row["label_id"]))


@when('I attempt to call "remove_label_from_card" with:')
def step_attempt_remove_label_from_card(context):
    from trello_mcp.tools.cards import remove_label_from_card
    row = context.table[0]
    capture_tool_error(context, remove_label_from_card(
        card_id=row["card_id"], label_id=row["label_id"]))
