import json
from trellio import TrelloAPIError
from trello_mcp.server import server, get_client
from trello_mcp.errors import handle_api_error


@server.tool(description="List all cards in a Trello list. Returns a JSON array with id, name, and desc for each card.")
async def list_cards(list_id: str) -> str:
    try:
        cards = await get_client().list_cards(list_id=list_id)
        return json.dumps([
            {"id": c.id, "name": c.name, "desc": c.description or ""}
            for c in cards
        ])
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Create a new card in a Trello list. Optionally set position (top/bottom), labels (comma-separated label IDs), due date (ISO 8601), and dueComplete (true/false). Returns the created card with id and name.")
async def create_card(list_id: str, name: str, desc: str = "", pos: str = "top", idLabels: str = "", due: str = "", dueComplete: str = "") -> str:
    try:
        kwargs = {"list_id": list_id, "name": name, "pos": pos}
        if desc:
            kwargs["desc"] = desc
        if idLabels:
            kwargs["idLabels"] = idLabels
        if due:
            kwargs["due"] = due
        if dueComplete:
            kwargs["dueComplete"] = dueComplete.lower() == "true"
        card = await get_client().create_card(**kwargs)
        return json.dumps({"id": card.id, "name": card.name})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Get a Trello card by ID. Returns card details including id, name, desc, idList, and idBoard.")
async def get_card(card_id: str) -> str:
    try:
        card = await get_client().get_card(card_id=card_id)
        return json.dumps({
            "id": card.id,
            "name": card.name,
            "desc": card.description or "",
            "idList": card.id_list,
            "idBoard": card.id_board or "",
        })
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Update a Trello card. Provide card_id and fields to update: name, desc, idList, pos (top/bottom/number), idLabels (comma-separated label IDs), due (ISO 8601), dueComplete (true/false). Returns the updated card.")
async def update_card(card_id: str, name: str = "", desc: str = "", idList: str = "", pos: str = "", idLabels: str = "", due: str = "", dueComplete: str = "") -> str:
    try:
        kwargs = {}
        if name:
            kwargs["name"] = name
        if desc:
            kwargs["desc"] = desc
        if idList:
            kwargs["idList"] = idList
        if pos:
            kwargs["pos"] = pos
        if due:
            kwargs["due"] = due
        if dueComplete:
            kwargs["dueComplete"] = dueComplete.lower() == "true"
        if idLabels:
            kwargs["idLabels"] = idLabels
        card = await get_client().update_card(card_id=card_id, **kwargs)
        return json.dumps({"id": card.id, "name": card.name})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Add an existing label to a Trello card.")
async def add_label_to_card(card_id: str, label_id: str) -> str:
    try:
        await get_client().add_label_to_card(card_id=card_id, label_id=label_id)
        return json.dumps({"success": True})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Remove a label from a Trello card.")
async def remove_label_from_card(card_id: str, label_id: str) -> str:
    try:
        await get_client().remove_label_from_card(card_id=card_id, label_id=label_id)
        return json.dumps({"success": True})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Delete a Trello card permanently. This action cannot be undone.")
async def delete_card(card_id: str) -> str:
    try:
        await get_client().delete_card(card_id=card_id)
        return json.dumps({"deleted": True})
    except TrelloAPIError as e:
        handle_api_error(e)
