import json
from trellio import TrelloAPIError
from trello_mcp.server import server, get_client
from trello_mcp.errors import handle_api_error


@server.tool(description="List all comments on a Trello card. Returns a JSON array with id and text for each comment.")
async def list_comments(card_id: str) -> str:
    try:
        comments = await get_client().list_comments(card_id=card_id)
        return json.dumps([
            {"id": c.id, "text": c.text}
            for c in comments
        ])
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Add a comment to a Trello card. Returns the created comment with id and text.")
async def add_comment(card_id: str, text: str) -> str:
    try:
        comment = await get_client().add_comment(card_id=card_id, text=text)
        return json.dumps({"id": comment.id, "text": comment.text})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Update a Trello comment. Returns the updated comment with id and text.")
async def update_comment(comment_id: str, text: str) -> str:
    try:
        comment = await get_client().update_comment(
            comment_id=comment_id, text=text,
        )
        return json.dumps({"id": comment.id, "text": comment.text})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Delete a Trello comment permanently.")
async def delete_comment(comment_id: str) -> str:
    try:
        await get_client().delete_comment(comment_id=comment_id)
        return json.dumps({"deleted": True})
    except TrelloAPIError as e:
        handle_api_error(e)
