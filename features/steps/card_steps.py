from behave import given, when
from trellio.models import TrelloCard, TrelloList
from steps.common_steps import run_async, capture_tool_error


@given('the Trello API returns cards for list "{list_id}":')
def step_api_returns_cards(context, list_id):
    cards = []
    for row in context.table:
        cards.append(TrelloCard(
            id=row["id"],
            name=row["name"],
            idList=list_id,
            desc=row.get("desc", ""),
        ))
    context.mock_client.list_cards.return_value = cards


@given('the Trello API will return a created card with id "{card_id}"')
def step_api_returns_created_card(context, card_id):
    async def mock_create(list_id, name, desc=None, pos="top", idLabels=None, due=None, dueComplete=None):
        return TrelloCard(id=card_id, name=name, idList=list_id, desc=desc or "")

    context.mock_client.create_card.side_effect = mock_create


@given('the Trello API returns card "{card_id}" with name "{name}" and desc "{desc}"')
def step_api_returns_card(context, card_id, name, desc):
    async def mock_get(card_id):
        return TrelloCard(id=card_id, name=name, idList="ls-000", desc=desc)

    context.mock_client.get_card.side_effect = mock_get


@given('the Trello API returns card "{card_id}" with name "{name}" desc "{desc}" and labels "{labels}"')
def step_api_returns_card_with_labels(context, card_id, name, desc, labels):
    label_ids = [l.strip() for l in labels.split(",")]

    async def mock_get(card_id):
        return TrelloCard(id=card_id, name=name, idList="ls-000", desc=desc, idLabels=label_ids)

    context.mock_client.get_card.side_effect = mock_get


@given('the Trello API returns cards with labels for list "{list_id}":')
def step_api_returns_cards_with_labels(context, list_id):
    cards = []
    for row in context.table:
        label_ids = [l.strip() for l in row["idLabels"].split(",")]
        cards.append(TrelloCard(
            id=row["id"], name=row["name"], idList=list_id, idLabels=label_ids,
        ))
    context.mock_client.list_cards.return_value = cards


@given('the Trello API will return an updated card with id "{card_id}" and name "{new_name}"')
def step_api_returns_updated_card(context, card_id, new_name):
    async def mock_update(card_id, **kwargs):
        return TrelloCard(
            id=card_id,
            name=kwargs.get("name", new_name),
            idList="ls-000",
        )

    context.mock_client.update_card.side_effect = mock_update


@given('the Trello API will accept card deletion')
def step_api_accepts_card_deletion(context):
    context.mock_client.delete_card.return_value = None


@when('I call the "list_cards" tool with list_id "{list_id}"')
def step_call_list_cards(context, list_id):
    from trello_mcp.tools.cards import list_cards
    context.result = run_async(list_cards(list_id=list_id))


def _setup_stateful_card_mock(context, card_id, name, initial_labels):
    """Stateful mock (§7.2): simulates trellio-client >=1.2.0 behavior
    where add/remove_label_to_card use read-modify-write via
    get_card + update_card internally."""
    card_labels = list(initial_labels)

    async def mock_get(card_id=card_id, **kwargs):
        return TrelloCard(id=card_id, name=name, idList="ls-000", idLabels=list(card_labels))

    async def mock_update(card_id=card_id, **kwargs):
        raw = kwargs.get("idLabels", "")
        card_labels[:] = [l for l in raw.split(",") if l] if raw else []
        return TrelloCard(id=card_id, name=name, idList="ls-000", idLabels=list(card_labels))

    async def mock_add_label(card_id=card_id, label_id=None, **kwargs):
        if label_id not in card_labels:
            card_labels.append(label_id)

    async def mock_remove_label(card_id=card_id, label_id=None, **kwargs):
        card_labels[:] = [l for l in card_labels if l != label_id]

    context.mock_client.get_card.side_effect = mock_get
    context.mock_client.update_card.side_effect = mock_update
    context.mock_client.add_label_to_card.side_effect = mock_add_label
    context.mock_client.remove_label_from_card.side_effect = mock_remove_label


@given('a card "{card_id}" exists with name "{name}" and no labels')
def step_card_exists_no_labels(context, card_id, name):
    _setup_stateful_card_mock(context, card_id, name, [])


@given('a card "{card_id}" exists with name "{name}" and labels "{label_csv}"')
def step_card_exists_with_labels(context, card_id, name, label_csv):
    _setup_stateful_card_mock(context, card_id, name,
                              [l.strip() for l in label_csv.split(",") if l.strip()])


@given('the Trello API will accept adding a label to a card')
def step_api_accepts_add_label(context):
    context.mock_client.add_label_to_card.return_value = None


@given('the Trello API will accept removing a label from a card')
def step_api_accepts_remove_label(context):
    context.mock_client.remove_label_from_card.return_value = None


@when('I call the "create_card" tool with:')
def step_call_create_card(context):
    from trello_mcp.tools.cards import create_card
    row = context.table[0]
    kwargs = {"list_id": row["list_id"], "name": row["name"]}
    if "desc" in context.table.headings:
        kwargs["desc"] = row["desc"]
    if "pos" in context.table.headings:
        kwargs["pos"] = row["pos"]
    if "idLabels" in context.table.headings:
        kwargs["idLabels"] = row["idLabels"]
    if "due" in context.table.headings:
        kwargs["due"] = row["due"]
    if "dueComplete" in context.table.headings:
        kwargs["dueComplete"] = row["dueComplete"]
    context.result = run_async(create_card(**kwargs))


@when('I call the "get_card" tool with card_id "{card_id}"')
def step_call_get_card(context, card_id):
    from trello_mcp.tools.cards import get_card
    context.result = run_async(get_card(card_id=card_id))


@when('I call the "update_card" tool with:')
def step_call_update_card(context):
    from trello_mcp.tools.cards import update_card
    row = context.table[0]
    kwargs = {h: row[h] for h in context.table.headings}
    context.result = run_async(update_card(**kwargs))


@when('I call the "add_label_to_card" tool with:')
def step_call_add_label_to_card(context):
    from trello_mcp.tools.cards import add_label_to_card
    row = context.table[0]
    context.result = run_async(add_label_to_card(
        card_id=row["card_id"], label_id=row["label_id"],
    ))


@when('I call the "remove_label_from_card" tool with:')
def step_call_remove_label_from_card(context):
    from trello_mcp.tools.cards import remove_label_from_card
    row = context.table[0]
    context.result = run_async(remove_label_from_card(
        card_id=row["card_id"], label_id=row["label_id"],
    ))


@when('I call the "delete_card" tool with card_id "{card_id}"')
def step_call_delete_card(context, card_id):
    from trello_mcp.tools.cards import delete_card
    context.result = run_async(delete_card(card_id=card_id))


@given('the Trello API will return an archived card with id "{card_id}"')
def step_api_returns_archived_card(context, card_id):
    async def mock_update(card_id, **kwargs):
        return TrelloCard(
            id=card_id, name="Archived", idList="ls-000",
            closed=kwargs.get("closed", True),
        )
    context.mock_client.update_card.side_effect = mock_update


@given('the Trello API will return an unarchived card with id "{card_id}"')
def step_api_returns_unarchived_card(context, card_id):
    async def mock_update(card_id, **kwargs):
        return TrelloCard(
            id=card_id, name="Active", idList="ls-000",
            closed=kwargs.get("closed", False),
        )
    context.mock_client.update_card.side_effect = mock_update


@when('I call the "archive_card" tool with card_id "{card_id}"')
def step_call_archive_card(context, card_id):
    from trello_mcp.tools.cards import archive_card
    context.result = run_async(archive_card(card_id=card_id))


@when('I call the "unarchive_card" tool with card_id "{card_id}"')
def step_call_unarchive_card(context, card_id):
    from trello_mcp.tools.cards import unarchive_card
    context.result = run_async(unarchive_card(card_id=card_id))


# --- Archived list validation ---

@given('the list "{list_id}" is archived with name "{name}"')
def step_list_is_archived(context, list_id, name):
    async def mock_get_list(list_id=list_id, **kwargs):
        return TrelloList(id=list_id, name=name, idBoard="bd-000", closed=True)
    context.mock_client.get_list.side_effect = mock_get_list


@given('the list "{list_id}" is active with name "{name}"')
def step_list_is_active(context, list_id, name):
    async def mock_get_list(list_id=list_id, **kwargs):
        return TrelloList(id=list_id, name=name, idBoard="bd-000", closed=False)
    context.mock_client.get_list.side_effect = mock_get_list


@when('I attempt to call "create_card" with:')
def step_attempt_create_card(context):
    from trello_mcp.tools.cards import create_card
    row = context.table[0]
    kwargs = {"list_id": row["list_id"], "name": row["name"]}
    capture_tool_error(context, create_card(**kwargs))


@when('I attempt to call "update_card" with:')
def step_attempt_update_card(context):
    from trello_mcp.tools.cards import update_card
    row = context.table[0]
    kwargs = {h: row[h] for h in context.table.headings}
    capture_tool_error(context, update_card(**kwargs))
