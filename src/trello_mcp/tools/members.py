import json
from trellio import TrelloAPIError
from trello_mcp.server import server, get_client
from trello_mcp.errors import handle_api_error


@server.tool(description="Get the authenticated Trello user. Returns id, username, and fullName.")
async def get_me() -> str:
    try:
        member = await get_client().get_me()
        return json.dumps(ensure_ascii=False, obj={
            "id": member.id,
            "username": member.username,
            "fullName": member.full_name,
        })
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="List all members of a Trello board. Returns a JSON array with id, username, and fullName.")
async def list_board_members(board_id: str) -> str:
    try:
        members = await get_client().list_board_members(board_id=board_id)
        return json.dumps(ensure_ascii=False, obj=[
            {"id": m.id, "username": m.username, "fullName": m.full_name}
            for m in members
        ])
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Get a Trello member by ID. Returns id, username, and fullName.")
async def get_member(member_id: str) -> str:
    try:
        member = await get_client().get_member(member_id=member_id)
        return json.dumps(ensure_ascii=False, obj={
            "id": member.id,
            "username": member.username,
            "fullName": member.full_name,
        })
    except TrelloAPIError as e:
        handle_api_error(e)
