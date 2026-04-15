import json
from trellio import TrelloAPIError
from trello_mcp.server import server, get_client
from trello_mcp.errors import handle_api_error
from trello_mcp.tools.validation import check_board_not_archived


@server.tool(description="List all lists on a Trello board. Returns a JSON array with id and name for each list.")
async def list_lists(board_id: str) -> str:
    try:
        lists = await get_client().list_lists(board_id=board_id)
        return json.dumps(ensure_ascii=False, obj=[
            {"id": l.id, "name": l.name}
            for l in lists
        ])
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Create a new list on a Trello board. Returns the created list with id and name.")
async def create_list(board_id: str, name: str) -> str:
    try:
        client = get_client()
        await check_board_not_archived(client, board_id)
        lst = await client.create_list(board_id=board_id, name=name)
        return json.dumps(ensure_ascii=False, obj={"id": lst.id, "name": lst.name})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Update a Trello list. Provide list_id and fields to update: name, pos (top/bottom/number). Returns the updated list.")
async def update_list(list_id: str, name: str = "", pos: str = "") -> str:
    try:
        kwargs = {}
        if name:
            kwargs["name"] = name
        if pos:
            kwargs["pos"] = pos
        lst = await get_client().update_list(list_id=list_id, **kwargs)
        return json.dumps(ensure_ascii=False, obj={"id": lst.id, "name": lst.name})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Archive a Trello list (set closed=true). This hides the list from the board.")
async def archive_list(list_id: str) -> str:
    try:
        lst = await get_client().update_list(list_id=list_id, closed=True)
        return json.dumps(ensure_ascii=False, obj={"id": lst.id, "closed": lst.closed})
    except TrelloAPIError as e:
        handle_api_error(e)
