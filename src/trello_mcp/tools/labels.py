import json
from trellio import TrelloAPIError
from trello_mcp.server import server, get_client
from trello_mcp.errors import handle_api_error
from trello_mcp.tools.validation import check_board_not_archived


@server.tool(description="List all labels on a Trello board. Returns a JSON array with id, name, and color for each label.")
async def list_board_labels(board_id: str) -> str:
    try:
        labels = await get_client().list_board_labels(board_id=board_id)
        return json.dumps(ensure_ascii=False, obj=[
            {"id": l.id, "name": l.name, "color": l.color}
            for l in labels
        ])
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Create a label on a Trello board. Returns the created label with id, name, and color.")
async def create_label(board_id: str, name: str, color: str) -> str:
    try:
        client = get_client()
        await check_board_not_archived(client, board_id)
        label = await client.create_label(
            name=name, color=color, board_id=board_id,
        )
        return json.dumps(ensure_ascii=False, obj={"id": label.id, "name": label.name, "color": label.color})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Update a Trello label. Provide label_id and fields to update (name, color). Returns the updated label.")
async def update_label(label_id: str, name: str = "", color: str = "") -> str:
    try:
        kwargs = {}
        if name:
            kwargs["name"] = name
        if color:
            kwargs["color"] = color
        label = await get_client().update_label(label_id=label_id, **kwargs)
        return json.dumps(ensure_ascii=False, obj={"id": label.id, "name": label.name, "color": label.color})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Delete a Trello label permanently.")
async def delete_label(label_id: str) -> str:
    try:
        await get_client().delete_label(label_id=label_id)
        return json.dumps(ensure_ascii=False, obj={"deleted": True})
    except TrelloAPIError as e:
        handle_api_error(e)
