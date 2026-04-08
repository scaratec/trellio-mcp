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


@server.tool(description="Create a new card in a Trello list. Returns the created card with id and name.")
async def create_card(list_id: str, name: str, desc: str = "") -> str:
    try:
        card = await get_client().create_card(
            list_id=list_id, name=name, desc=desc or None,
        )
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


@server.tool(description="Update a Trello card. Provide card_id and any fields to update (name, desc, idList). Returns the updated card.")
async def update_card(card_id: str, name: str = "", desc: str = "", idList: str = "") -> str:
    try:
        kwargs = {}
        if name:
            kwargs["name"] = name
        if desc:
            kwargs["desc"] = desc
        if idList:
            kwargs["idList"] = idList
        card = await get_client().update_card(card_id=card_id, **kwargs)
        return json.dumps({"id": card.id, "name": card.name})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Delete a Trello card permanently. This action cannot be undone.")
async def delete_card(card_id: str) -> str:
    try:
        await get_client().delete_card(card_id=card_id)
        return json.dumps({"deleted": True})
    except TrelloAPIError as e:
        handle_api_error(e)
