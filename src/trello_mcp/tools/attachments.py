import json
from trellio import TrelloAPIError
from trello_mcp.server import server, get_client
from trello_mcp.errors import handle_api_error


@server.tool(description="List all attachments on a Trello card. Returns a JSON array with id, name, and url.")
async def list_attachments(card_id: str) -> str:
    try:
        attachments = await get_client().list_attachments(card_id=card_id)
        return json.dumps([
            {"id": a.id, "name": a.name, "url": a.url}
            for a in attachments
        ])
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Create an attachment on a Trello card by URL. Returns the created attachment with id, name, and url.")
async def create_attachment(card_id: str, url: str, name: str = "") -> str:
    try:
        att = await get_client().create_attachment(
            card_id=card_id, url=url, name=name or None,
        )
        return json.dumps({"id": att.id, "name": att.name, "url": att.url})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Delete an attachment from a Trello card.")
async def delete_attachment(card_id: str, attachment_id: str) -> str:
    try:
        await get_client().delete_attachment(
            card_id=card_id, attachment_id=attachment_id,
        )
        return json.dumps({"deleted": True})
    except TrelloAPIError as e:
        handle_api_error(e)
