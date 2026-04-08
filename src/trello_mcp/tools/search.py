import json
from trellio import TrelloAPIError
from trello_mcp.server import server, get_client
from trello_mcp.errors import handle_api_error


@server.tool(description="Search Trello for boards and cards by keyword. Returns matching boards and cards.")
async def search(query: str, limit: int = 10) -> str:
    try:
        result = await get_client().search(query=query, limit=limit)
        return json.dumps({
            "boards": [
                {"id": b.id, "name": b.name}
                for b in result.boards
            ],
            "cards": [
                {"id": c.id, "name": c.name, "idBoard": c.id_board or ""}
                for c in result.cards
            ],
        })
    except TrelloAPIError as e:
        handle_api_error(e)
