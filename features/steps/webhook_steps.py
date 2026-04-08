from behave import given, when
from trellio.models import TrelloWebhook
from steps.common_steps import run_async


@given('the Trello API returns webhooks:')
def step_api_returns_webhooks(context):
    webhooks = []
    for row in context.table:
        webhooks.append(TrelloWebhook(
            id=row["id"], description=row["description"],
            callbackURL=row["callbackURL"],
            active=row["active"].lower() == "true",
            idModel="bd-000",
        ))
    context.mock_client.list_webhooks.return_value = webhooks


@given('the Trello API will return a created webhook with id "{wh_id}"')
def step_api_returns_created_webhook(context, wh_id):
    async def mock_create(callback_url, id_model, description=None):
        return TrelloWebhook(
            id=wh_id, callbackURL=callback_url,
            idModel=id_model, description=description,
        )
    context.mock_client.create_webhook.side_effect = mock_create


@given('the Trello API returns webhook "{wh_id}" with description "{desc}" and callback_url "{url}"')
def step_api_returns_webhook(context, wh_id, desc, url):
    async def mock_get(webhook_id):
        return TrelloWebhook(
            id=webhook_id, description=desc,
            callbackURL=url, idModel="bd-000",
        )
    context.mock_client.get_webhook.side_effect = mock_get


@given('the Trello API will return an updated webhook with id "{wh_id}" and description "{desc}"')
def step_api_returns_updated_webhook(context, wh_id, desc):
    async def mock_update(webhook_id, **kwargs):
        return TrelloWebhook(
            id=webhook_id, description=kwargs.get("description", desc),
            callbackURL="https://example.com/hook", idModel="bd-000",
        )
    context.mock_client.update_webhook.side_effect = mock_update


@given('the Trello API will accept webhook deletion')
def step_api_accepts_webhook_deletion(context):
    context.mock_client.delete_webhook.return_value = None


@when('I call the "list_webhooks" tool')
def step_call_list_webhooks(context):
    from trello_mcp.tools.webhooks import list_webhooks
    context.result = run_async(list_webhooks())


@when('I call the "create_webhook" tool with:')
def step_call_create_webhook(context):
    from trello_mcp.tools.webhooks import create_webhook
    row = context.table[0]
    context.result = run_async(create_webhook(
        callback_url=row["callback_url"],
        id_model=row["id_model"],
        description=row.get("description", ""),
    ))


@when('I call the "get_webhook" tool with webhook_id "{wh_id}"')
def step_call_get_webhook(context, wh_id):
    from trello_mcp.tools.webhooks import get_webhook
    context.result = run_async(get_webhook(webhook_id=wh_id))


@when('I call the "update_webhook" tool with:')
def step_call_update_webhook(context):
    from trello_mcp.tools.webhooks import update_webhook
    row = context.table[0]
    kwargs = {h: row[h] for h in context.table.headings}
    context.result = run_async(update_webhook(**kwargs))


@when('I call the "delete_webhook" tool with webhook_id "{wh_id}"')
def step_call_delete_webhook(context, wh_id):
    from trello_mcp.tools.webhooks import delete_webhook
    context.result = run_async(delete_webhook(webhook_id=wh_id))
