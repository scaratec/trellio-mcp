import json
from trellio import TrelloAPIError
from trello_mcp.server import server, get_client
from trello_mcp.errors import handle_api_error
from trello_mcp.tools.validation import check_card_not_archived


@server.tool(description="List all checklists on a Trello card. Returns a JSON array with id and name for each checklist.")
async def list_card_checklists(card_id: str) -> str:
    try:
        checklists = await get_client().list_card_checklists(card_id=card_id)
        return json.dumps(ensure_ascii=False, obj=[
            {"id": cl.id, "name": cl.name}
            for cl in checklists
        ])
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Create a checklist on a Trello card. Returns the created checklist with id and name.")
async def create_checklist(card_id: str, name: str) -> str:
    try:
        client = get_client()
        await check_card_not_archived(client, card_id)
        cl = await client.create_checklist(card_id=card_id, name=name)
        return json.dumps(ensure_ascii=False, obj={"id": cl.id, "name": cl.name})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Delete a Trello checklist permanently.")
async def delete_checklist(checklist_id: str) -> str:
    try:
        await get_client().delete_checklist(checklist_id=checklist_id)
        return json.dumps(ensure_ascii=False, obj={"deleted": True})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Create a check item in a Trello checklist. Optionally set position (top/bottom/numeric). Returns the created item with id, name, and state.")
async def create_check_item(checklist_id: str, name: str, pos: str = "") -> str:
    try:
        kwargs = {"checklist_id": checklist_id, "name": name}
        if pos:
            kwargs["pos"] = pos
        item = await get_client().create_check_item(**kwargs)
        return json.dumps(ensure_ascii=False, obj={"id": item.id, "name": item.name, "state": item.state})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Update a check item. Provide card_id, check_item_id, and at least one of: state (complete/incomplete), name, pos (top/bottom/numeric).")
async def update_check_item(card_id: str, check_item_id: str, state: str = "", name: str = "", pos: str = "") -> str:
    try:
        kwargs = {"card_id": card_id, "check_item_id": check_item_id}
        if state:
            kwargs["state"] = state
        if name:
            kwargs["name"] = name
        if pos:
            kwargs["pos"] = pos
        item = await get_client().update_check_item(**kwargs)
        return json.dumps(ensure_ascii=False, obj={"id": item.id, "name": item.name, "state": item.state})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Delete a check item from a checklist.")
async def delete_check_item(checklist_id: str, check_item_id: str) -> str:
    try:
        await get_client().delete_check_item(
            checklist_id=checklist_id, check_item_id=check_item_id,
        )
        return json.dumps(ensure_ascii=False, obj={"deleted": True})
    except TrelloAPIError as e:
        handle_api_error(e)
