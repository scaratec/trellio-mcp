import json
from trellio import TrelloAPIError
from trello_mcp.server import server, get_client
from trello_mcp.errors import handle_api_error


@server.tool(description="Search Trello for boards and cards by keyword. Optional id_board scopes the search to a single board. Returns matching boards and cards (cards include idList, desc, idLabels).")
async def search(query: str, limit: int = 10, id_board: str = "") -> str:
    try:
        kwargs = {"query": query, "limit": limit}
        if id_board:
            kwargs["id_boards"] = id_board
        result = await get_client().search(**kwargs)
        return json.dumps(ensure_ascii=False, obj={
            "boards": [
                {"id": b.id, "name": b.name}
                for b in result.boards
            ],
            "cards": [
                {
                    "id": c.id,
                    "name": c.name,
                    "idBoard": c.id_board or "",
                    "idList": c.id_list,
                    "desc": c.description or "",
                    "idLabels": c.id_labels,
                }
                for c in result.cards
            ],
        })
    except TrelloAPIError as e:
        handle_api_error(e)
