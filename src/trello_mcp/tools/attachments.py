import json
import os
from pathlib import Path
from trellio import TrelloAPIError
from mcp.server.fastmcp.exceptions import ToolError
from trello_mcp.server import server, get_client
from trello_mcp.errors import handle_api_error
from trello_mcp.tools.validation import check_card_not_archived


@server.tool(description="List all attachments on a Trello card. Returns a JSON array with id, name, and url.")
async def list_attachments(card_id: str) -> str:
    try:
        attachments = await get_client().list_attachments(card_id=card_id)
        return json.dumps(ensure_ascii=False, obj=[
            {"id": a.id, "name": a.name, "url": a.url}
            for a in attachments
        ])
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Create an attachment on a Trello card by URL. Returns the created attachment with id, name, and url.")
async def create_attachment(card_id: str, url: str, name: str = "") -> str:
    try:
        client = get_client()
        await check_card_not_archived(client, card_id)
        att = await client.create_attachment(
            card_id=card_id, url=url, name=name or None,
        )
        return json.dumps(ensure_ascii=False, obj={"id": att.id, "name": att.name, "url": att.url})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Get metadata for a single attachment on a Trello card. Returns the attachment with id, name, and url.")
async def get_attachment(card_id: str, attachment_id: str) -> str:
    try:
        att = await get_client().get_attachment(
            card_id=card_id, attachment_id=attachment_id,
        )
        return json.dumps(ensure_ascii=False, obj={"id": att.id, "name": att.name, "url": att.url})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Upload a local file as an attachment to a Trello card. Returns the created attachment with id, name, and url.")
async def upload_attachment(card_id: str, file_path: str, name: str = "") -> str:
    path = Path(file_path)
    if not path.exists():
        raise ToolError(f"File does not exist: {file_path}")
    if not path.is_file():
        raise ToolError(f"Path is not a regular file: {file_path}")
    if not os.access(file_path, os.R_OK):
        raise ToolError(f"File is not readable: {file_path}")
    try:
        client = get_client()
        await check_card_not_archived(client, card_id)
        att = await client.upload_attachment(
            card_id=card_id, file_path=file_path, name=name or None,
        )
        return json.dumps(ensure_ascii=False, obj={"id": att.id, "name": att.name, "url": att.url})
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Download a Trello card attachment to a local file. Returns the attachment metadata and the local file path.")
async def download_attachment(card_id: str, attachment_id: str, target_path: str) -> str:
    path = Path(target_path)
    if path.is_dir():
        raise ToolError(f"Target path is a directory: {target_path}")
    if not path.parent.exists():
        raise ToolError(f"Target directory does not exist: {path.parent}")
    try:
        client = get_client()
        att = await client.download_attachment(
            card_id=card_id, attachment_id=attachment_id, target_path=target_path,
        )
        return json.dumps(ensure_ascii=False, obj={
            "id": att.id, "name": att.name, "url": att.url, "path": target_path,
        })
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Delete an attachment from a Trello card.")
async def delete_attachment(card_id: str, attachment_id: str) -> str:
    try:
        await get_client().delete_attachment(
            card_id=card_id, attachment_id=attachment_id,
        )
        return json.dumps(ensure_ascii=False, obj={"deleted": True})
    except TrelloAPIError as e:
        handle_api_error(e)
