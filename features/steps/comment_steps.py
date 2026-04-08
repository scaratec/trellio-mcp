from behave import given, when
from trellio.models import TrelloComment
from steps.common_steps import run_async


@given('the Trello API returns comments for card "{card_id}":')
def step_api_returns_comments(context, card_id):
    comments = []
    for row in context.table:
        comments.append(TrelloComment(id=row["id"], text=row["text"]))
    context.mock_client.list_comments.return_value = comments


@given('the Trello API will return a created comment with id "{cm_id}"')
def step_api_returns_created_comment(context, cm_id):
    async def mock_add(card_id, text):
        return TrelloComment(id=cm_id, text=text)
    context.mock_client.add_comment.side_effect = mock_add


@given('the Trello API will return an updated comment with id "{cm_id}" and text "{text}"')
def step_api_returns_updated_comment(context, cm_id, text):
    async def mock_update(comment_id, text):
        return TrelloComment(id=comment_id, text=text)
    context.mock_client.update_comment.side_effect = mock_update


@given('the Trello API will accept comment deletion')
def step_api_accepts_comment_deletion(context):
    context.mock_client.delete_comment.return_value = None


@when('I call the "list_comments" tool with card_id "{card_id}"')
def step_call_list_comments(context, card_id):
    from trello_mcp.tools.comments import list_comments
    context.result = run_async(list_comments(card_id=card_id))


@when('I call the "add_comment" tool with:')
def step_call_add_comment(context):
    from trello_mcp.tools.comments import add_comment
    row = context.table[0]
    context.result = run_async(add_comment(
        card_id=row["card_id"], text=row["text"],
    ))


@when('I call the "update_comment" tool with:')
def step_call_update_comment(context):
    from trello_mcp.tools.comments import update_comment
    row = context.table[0]
    context.result = run_async(update_comment(
        comment_id=row["comment_id"], text=row["text"],
    ))


@when('I call the "delete_comment" tool with comment_id "{cm_id}"')
def step_call_delete_comment(context, cm_id):
    from trello_mcp.tools.comments import delete_comment
    context.result = run_async(delete_comment(comment_id=cm_id))
