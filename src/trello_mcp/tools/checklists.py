import json
from trellio import TrelloAPIError
from trello_mcp.server import server, get_client
from trello_mcp.errors import handle_api_error


@server.tool(description="List all checklists on a Trello card. Returns a JSON array with id and name for each checklist.")
async def list_card_checklists(card_id: str) -> str:
    try:
        checklists = await get_client().list_card_checklists(card_id=card_id)
        return json.dumps([
            {"id": cl.id, "name": cl.name}
            for cl in checklists
        ])
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Create a checklist on a Trello card. Returns the created checklist with id and name.")
async def create_checklist(card_id: str, name: str) -> str:
    try:
        cl = await get_client().create_checklist(card_id=card_id, name=name)
        return json.dumps({"id": cl.id, "name": cl.name})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Delete a Trello checklist permanently.")
async def delete_checklist(checklist_id: str) -> str:
    try:
        await get_client().delete_checklist(checklist_id=checklist_id)
        return json.dumps({"deleted": True})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Create a check item in a Trello checklist. Returns the created item with id, name, and state.")
async def create_check_item(checklist_id: str, name: str) -> str:
    try:
        item = await get_client().create_check_item(
            checklist_id=checklist_id, name=name,
        )
        return json.dumps({"id": item.id, "name": item.name, "state": item.state})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Update a check item state (complete/incomplete). Requires both card_id and check_item_id.")
async def update_check_item(card_id: str, check_item_id: str, state: str) -> str:
    try:
        item = await get_client().update_check_item(
            card_id=card_id, check_item_id=check_item_id, state=state,
        )
        return json.dumps({"id": item.id, "name": item.name, "state": item.state})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Delete a check item from a checklist.")
async def delete_check_item(checklist_id: str, check_item_id: str) -> str:
    try:
        await get_client().delete_check_item(
            checklist_id=checklist_id, check_item_id=check_item_id,
        )
        return json.dumps({"deleted": True})
    except TrelloAPIError as e:
        handle_api_error(e)
