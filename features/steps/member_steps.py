from behave import given, when
from trellio.models import TrelloMember
from steps.common_steps import run_async


@given('the Trello API returns me with id "{mid}" username "{username}" and full_name "{full_name}"')
def step_api_returns_me(context, mid, username, full_name):
    async def mock_get_me():
        return TrelloMember(id=mid, username=username, fullName=full_name)
    context.mock_client.get_me.side_effect = mock_get_me


@given('the Trello API returns members for board "{board_id}":')
def step_api_returns_members(context, board_id):
    members = []
    for row in context.table:
        members.append(TrelloMember(
            id=row["id"], username=row["username"],
            fullName=row["full_name"],
        ))
    context.mock_client.list_board_members.return_value = members


@given('the Trello API returns member "{member_id}" with username "{username}" and full_name "{full_name}"')
def step_api_returns_member(context, member_id, username, full_name):
    async def mock_get(member_id):
        return TrelloMember(id=member_id, username=username, fullName=full_name)
    context.mock_client.get_member.side_effect = mock_get


@when('I call the "get_me" tool')
def step_call_get_me(context):
    from trello_mcp.tools.members import get_me
    context.result = run_async(get_me())


@when('I call the "list_board_members" tool with board_id "{board_id}"')
def step_call_list_board_members(context, board_id):
    from trello_mcp.tools.members import list_board_members
    context.result = run_async(list_board_members(board_id=board_id))


@when('I call the "get_member" tool with member_id "{member_id}"')
def step_call_get_member(context, member_id):
    from trello_mcp.tools.members import get_member
    context.result = run_async(get_member(member_id=member_id))
