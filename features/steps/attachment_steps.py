from behave import given, when
from trellio.models import TrelloAttachment
from steps.common_steps import run_async


@given('the Trello API returns attachments for card "{card_id}":')
def step_api_returns_attachments(context, card_id):
    attachments = []
    for row in context.table:
        attachments.append(TrelloAttachment(
            id=row["id"], name=row["name"], url=row["url"],
        ))
    context.mock_client.list_attachments.return_value = attachments


@given('the Trello API will return a created attachment with id "{att_id}"')
def step_api_returns_created_attachment(context, att_id):
    async def mock_create(card_id, url, name=None):
        return TrelloAttachment(id=att_id, name=name or "", url=url)
    context.mock_client.create_attachment.side_effect = mock_create


@given('a card "{card_id}" has no attachments')
def step_card_has_no_attachments(context, card_id):
    """Stateful mock (§7.2): accumulates attachments on create,
    returns them on list."""
    store = []
    counter = [0]

    async def mock_create(card_id, url, name=None):
        counter[0] += 1
        att = TrelloAttachment(
            id=f"at-auto-{counter[0]}", name=name or "", url=url,
        )
        store.append(att)
        return att

    async def mock_list(card_id=card_id, **kwargs):
        return list(store)

    context.mock_client.create_attachment.side_effect = mock_create
    context.mock_client.list_attachments.side_effect = mock_list


@given('a card "{card_id}" has attachments:')
def step_card_has_attachments(context, card_id):
    """Stateful mock (§7.2): pre-populated, removes on delete,
    returns remainder on list."""
    store = []
    for row in context.table:
        store.append(TrelloAttachment(
            id=row["id"], name=row["name"], url=row["url"],
        ))

    async def mock_delete(card_id=card_id, attachment_id=None, **kw):
        store[:] = [a for a in store if a.id != attachment_id]

    async def mock_list(card_id=card_id, **kwargs):
        return list(store)

    context.mock_client.delete_attachment.side_effect = mock_delete
    context.mock_client.list_attachments.side_effect = mock_list


@given('the Trello API will accept attachment deletion')
def step_api_accepts_attachment_deletion(context):
    context.mock_client.delete_attachment.return_value = None


@when('I call the "list_attachments" tool with card_id "{card_id}"')
def step_call_list_attachments(context, card_id):
    from trello_mcp.tools.attachments import list_attachments
    context.result = run_async(list_attachments(card_id=card_id))


@when('I call the "create_attachment" tool with:')
def step_call_create_attachment(context):
    from trello_mcp.tools.attachments import create_attachment
    row = context.table[0]
    context.result = run_async(create_attachment(
        card_id=row["card_id"], url=row["url"], name=row.get("name", ""),
    ))


@given('the Trello API returns attachment "{att_id}" for card "{card_id}":')
def step_api_returns_single_attachment(context, att_id, card_id):
    row = context.table[0]
    att = TrelloAttachment(id=row["id"], name=row["name"], url=row["url"])

    async def mock_get(card_id, attachment_id, **kwargs):
        return att
    context.mock_client.get_attachment.side_effect = mock_get


@when('I call the "get_attachment" tool with card_id "{card_id}" and attachment_id "{att_id}"')
def step_call_get_attachment(context, card_id, att_id):
    from trello_mcp.tools.attachments import get_attachment
    context.result = run_async(get_attachment(card_id=card_id, attachment_id=att_id))


@when('I call the "delete_attachment" tool with:')
def step_call_delete_attachment(context):
    from trello_mcp.tools.attachments import delete_attachment
    row = context.table[0]
    context.result = run_async(delete_attachment(
        card_id=row["card_id"], attachment_id=row["attachment_id"],
    ))
