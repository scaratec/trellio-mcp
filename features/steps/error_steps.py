from behave import given, when, then
from trellio import TrelloAPIError
from mcp.server.fastmcp.exceptions import ToolError
from steps.common_steps import run_async


@given('the Trello API will fail with status {status:d} and message "{message}"')
def step_api_will_fail(context, status, message):
    context.mock_client.list_boards.side_effect = TrelloAPIError(status, message)


@given('the Trello API will timeout with message "{message}"')
def step_api_will_timeout(context, message):
    context.mock_client.list_boards.side_effect = TrelloAPIError(0, message)


@given('the Trello API will fail on get_board with status {status:d} and message "{message}"')
def step_api_fail_get_board(context, status, message):
    context.mock_client.get_board.side_effect = TrelloAPIError(status, message)


@given('the Trello API will fail on get_card with status {status:d} and message "{message}"')
def step_api_fail_get_card(context, status, message):
    context.mock_client.get_card.side_effect = TrelloAPIError(status, message)


@given('the Trello API will fail on list_cards with status {status:d} and message "{message}"')
def step_api_fail_list_cards(context, status, message):
    context.mock_client.list_cards.side_effect = TrelloAPIError(status, message)


@given('the Trello API will fail on get_attachment with status {status:d} and message "{message}"')
def step_api_fail_get_attachment(context, status, message):
    context.mock_client.get_attachment.side_effect = TrelloAPIError(status, message)
    context.mock_client.download_attachment.side_effect = TrelloAPIError(status, message)


@when('I attempt to call the "list_boards" tool')
def step_attempt_list_boards(context):
    from trello_mcp.tools.boards import list_boards
    try:
        context.result = run_async(list_boards())
        context.error = None
    except ToolError as e:
        context.error = e
        context.result = None


@when('I attempt to call the "get_board_overview" tool with board_id "{board_id}"')
def step_attempt_get_board_overview(context, board_id):
    from trello_mcp.tools.boards import get_board_overview
    try:
        context.result = run_async(get_board_overview(board_id=board_id))
        context.error = None
    except ToolError as e:
        context.error = e
        context.result = None


@when('I attempt to read the resource "{uri}"')
def step_attempt_read_resource(context, uri):
    from trello_mcp.resources import read_board_resource, read_card_resource
    try:
        if "board" in uri:
            rid = uri.split("/")[-1]
            context.resource_result = run_async(read_board_resource(rid))
        else:
            rid = uri.split("/")[-1]
            context.resource_result = run_async(read_card_resource(rid))
        context.resource_error = None
    except (TrelloAPIError, Exception) as e:
        context.resource_error = e
        context.resource_result = None


@then('the tool should raise an error')
def step_tool_raised_error(context):
    assert context.error is not None, "Expected ToolError but none was raised"


@then('the error message should contain "{fragment}"')
def step_error_message_contains(context, fragment):
    msg = str(context.error)
    assert fragment in msg, f"Expected '{fragment}' in error: {msg}"


@then('the resource read should raise an error')
def step_resource_raised_error(context):
    assert context.resource_error is not None, "Expected error but none was raised"
