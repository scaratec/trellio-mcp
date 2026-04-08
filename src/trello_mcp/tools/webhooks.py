import json
from trellio import TrelloAPIError
from trello_mcp.server import server, get_client
from trello_mcp.errors import handle_api_error


@server.tool(description="List all Trello webhooks. Returns a JSON array with id, description, callbackURL, and active status.")
async def list_webhooks() -> str:
    try:
        webhooks = await get_client().list_webhooks()
        return json.dumps([
            {
                "id": w.id,
                "description": w.description or "",
                "callbackURL": w.callback_url,
                "active": w.active,
            }
            for w in webhooks
        ])
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Create a Trello webhook. Returns the created webhook with id and callbackURL.")
async def create_webhook(callback_url: str, id_model: str, description: str = "") -> str:
    try:
        wh = await get_client().create_webhook(
            callback_url=callback_url,
            id_model=id_model,
            description=description or None,
        )
        return json.dumps({
            "id": wh.id,
            "callbackURL": wh.callback_url,
        })
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Get a Trello webhook by ID. Returns webhook details including id, description, callbackURL, and active.")
async def get_webhook(webhook_id: str) -> str:
    try:
        wh = await get_client().get_webhook(webhook_id=webhook_id)
        return json.dumps({
            "id": wh.id,
            "description": wh.description or "",
            "callbackURL": wh.callback_url,
            "active": wh.active,
        })
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Update a Trello webhook. Provide webhook_id and fields to update (description, active).")
async def update_webhook(webhook_id: str, description: str = "", active: str = "") -> str:
    try:
        kwargs = {}
        if description:
            kwargs["description"] = description
        if active:
            kwargs["active"] = active.lower() == "true"
        wh = await get_client().update_webhook(webhook_id=webhook_id, **kwargs)
        return json.dumps({
            "id": wh.id,
            "description": wh.description or "",
        })
    except TrelloAPIError as e:
        handle_api_error(e)


@server.tool(description="Delete a Trello webhook permanently.")
async def delete_webhook(webhook_id: str) -> str:
    try:
        await get_client().delete_webhook(webhook_id=webhook_id)
        return json.dumps({"deleted": True})
    except TrelloAPIError as e:
        handle_api_error(e)
