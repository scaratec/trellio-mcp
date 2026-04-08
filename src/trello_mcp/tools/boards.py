import json
from trellio import TrelloAPIError
from trello_mcp.server import server, get_client
from trello_mcp.errors import handle_api_error


@server.tool(description="List all open Trello boards. Returns a JSON array of boards with id, name, and closed status.")
async def list_boards() -> str:
    try:
        boards = await get_client().list_boards()
        return json.dumps(ensure_ascii=False, obj=[
            {"id": b.id, "name": b.name, "closed": b.closed}
            for b in boards
        ])
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Create a new Trello board. Returns the created board with id and name.")
async def create_board(name: str, description: str = "") -> str:
    try:
        board = await get_client().create_board(name=name, description=description or None)
        return json.dumps(ensure_ascii=False, obj={"id": board.id, "name": board.name})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Get a Trello board by ID. Returns board details including id, name, description, and closed status.")
async def get_board(board_id: str) -> str:
    try:
        board = await get_client().get_board(board_id=board_id)
        return json.dumps(ensure_ascii=False, obj={
            "id": board.id,
            "name": board.name,
            "description": board.description or "",
            "closed": board.closed,
        })
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Update a Trello board. Provide board_id and any fields to update (name, description). Returns the updated board.")
async def update_board(board_id: str, name: str = "", description: str = "") -> str:
    try:
        kwargs = {}
        if name:
            kwargs["name"] = name
        if description:
            kwargs["description"] = description
        board = await get_client().update_board(board_id=board_id, **kwargs)
        return json.dumps(ensure_ascii=False, obj={"id": board.id, "name": board.name})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Get a complete board overview with all lists and their cards in a single call. Returns board details, lists, and nested cards.")
async def get_board_overview(board_id: str) -> str:
    try:
        client = get_client()
        board = await client.get_board(board_id=board_id)
        lists = await client.list_lists(board_id=board_id)
        result_lists = []
        for lst in lists:
            cards = await client.list_cards(list_id=lst.id)
            result_lists.append({
                "id": lst.id,
                "name": lst.name,
                "cards": [
                    {"id": c.id, "name": c.name, "desc": c.description or ""}
                    for c in cards
                ],
            })
        return json.dumps(ensure_ascii=False, obj={
            "board": {"id": board.id, "name": board.name},
            "lists": result_lists,
        })
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Delete a Trello board permanently. This action cannot be undone.")
async def delete_board(board_id: str) -> str:
    try:
        await get_client().delete_board(board_id=board_id)
        return json.dumps(ensure_ascii=False, obj={"deleted": True})
    except TrelloAPIError as e:
        handle_api_error(e)
