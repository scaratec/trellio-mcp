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


@given('the Trello API will fail on {method} with status {status:d} and message "{message}"')
def step_api_fail_on_method(context, method, status, message):
    """Arm exactly the method the step text names, and no other.

    One parameterised step instead of one per method, because the per-method
    variants were five copies of the same line that could drift apart from
    their own step text - and one of them had. The get_attachment variant also
    armed download_attachment, a method its text never mentioned; since
    download_attachment never calls get_attachment, the unnamed half was the
    only half that ever did anything. A scenario reading "will fail on
    get_attachment" therefore described a different event than the one that
    took place (guidelines 1.3 and 2.2). Taking the method name from the text
    makes that class of drift impossible: what the scenario says is what the
    step does.

    The mock carries the client's spec, so a name that TrellioClient does not
    have cannot silently arm nothing.
    """
    try:
        target = getattr(context.mock_client, method)
    except AttributeError:
        raise AssertionError(
            f'TrellioClient has no method "{method}", so this step would arm a '
            f'failure that nothing can ever reach. Correct the method name in '
            f'the feature file.') from None
    target.side_effect = TrelloAPIError(status, message)


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
