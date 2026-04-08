from behave import given, when
from trellio.models import TrelloChecklist, TrelloCheckItem
from steps.common_steps import run_async


@given('the Trello API returns checklists for card "{card_id}":')
def step_api_returns_checklists(context, card_id):
    checklists = []
    for row in context.table:
        checklists.append(TrelloChecklist(
            id=row["id"], name=row["name"], idCard=card_id,
        ))
    context.mock_client.list_card_checklists.return_value = checklists


@given('the Trello API will return a created checklist with id "{cl_id}"')
def step_api_returns_created_checklist(context, cl_id):
    async def mock_create(card_id, name):
        return TrelloChecklist(id=cl_id, name=name, idCard=card_id)
    context.mock_client.create_checklist.side_effect = mock_create


@given('the Trello API will accept checklist deletion')
def step_api_accepts_checklist_deletion(context):
    context.mock_client.delete_checklist.return_value = None


@given('the Trello API will return a created check item with id "{ci_id}"')
def step_api_returns_created_check_item(context, ci_id):
    async def mock_create(checklist_id, name):
        return TrelloCheckItem(id=ci_id, name=name, state="incomplete")
    context.mock_client.create_check_item.side_effect = mock_create


@given('the Trello API will return an updated check item with id "{ci_id}" name "{name}" and state "{state}"')
def step_api_returns_updated_check_item(context, ci_id, name, state):
    async def mock_update(card_id, check_item_id, state):
        return TrelloCheckItem(id=check_item_id, name=name, state=state)
    context.mock_client.update_check_item.side_effect = mock_update


@given('the Trello API will accept check item deletion')
def step_api_accepts_check_item_deletion(context):
    context.mock_client.delete_check_item.return_value = None


@when('I call the "list_card_checklists" tool with card_id "{card_id}"')
def step_call_list_card_checklists(context, card_id):
    from trello_mcp.tools.checklists import list_card_checklists
    context.result = run_async(list_card_checklists(card_id=card_id))


@when('I call the "create_checklist" tool with:')
def step_call_create_checklist(context):
    from trello_mcp.tools.checklists import create_checklist
    row = context.table[0]
    context.result = run_async(create_checklist(
        card_id=row["card_id"], name=row["name"],
    ))


@when('I call the "delete_checklist" tool with checklist_id "{cl_id}"')
def step_call_delete_checklist(context, cl_id):
    from trello_mcp.tools.checklists import delete_checklist
    context.result = run_async(delete_checklist(checklist_id=cl_id))


@when('I call the "create_check_item" tool with:')
def step_call_create_check_item(context):
    from trello_mcp.tools.checklists import create_check_item
    row = context.table[0]
    context.result = run_async(create_check_item(
        checklist_id=row["checklist_id"], name=row["name"],
    ))


@when('I call the "update_check_item" tool with:')
def step_call_update_check_item(context):
    from trello_mcp.tools.checklists import update_check_item
    row = context.table[0]
    context.result = run_async(update_check_item(
        card_id=row["card_id"],
        check_item_id=row["check_item_id"],
        state=row["state"],
    ))


@when('I call the "delete_check_item" tool with:')
def step_call_delete_check_item(context):
    from trello_mcp.tools.checklists import delete_check_item
    row = context.table[0]
    context.result = run_async(delete_check_item(
        checklist_id=row["checklist_id"],
        check_item_id=row["check_item_id"],
    ))
