import json
from trellio import TrelloAPIError
from trello_mcp.server import server, get_client
from trello_mcp.errors import handle_api_error


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
        lst = await get_client().create_list(board_id=board_id, name=name)
        return json.dumps(ensure_ascii=False, obj={"id": lst.id, "name": lst.name})
    except TrelloAPIError as e:
        handle_api_error(e)
