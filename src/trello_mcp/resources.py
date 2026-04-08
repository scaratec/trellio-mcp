import json
from trello_mcp.server import server, get_client


@server.resource("trello://board/{board_id}")
async def board_resource(board_id: str) -> str:
    return await read_board_resource(board_id)


@server.resource("trello://card/{card_id}")
async def card_resource(card_id: str) -> str:
    return await read_card_resource(card_id)


async def read_board_resource(board_id: str) -> str:
    client = get_client()
    board = await client.get_board(board_id=board_id)
    lists = await client.list_lists(board_id=board_id)
    result_lists = []
    for lst in lists:
        cards = await client.list_cards(list_id=lst.id)
        result_lists.append({
            "id": lst.id,
            "name": lst.name,
            "cards": [{"id": c.id, "name": c.name} for c in cards],
        })
    return json.dumps(ensure_ascii=False, obj={
        "board": {"id": board.id, "name": board.name},
        "lists": result_lists,
    })


async def read_card_resource(card_id: str) -> str:
    client = get_client()
    card = await client.get_card(card_id=card_id)
    checklists = await client.list_card_checklists(card_id=card_id)
    comments = await client.list_comments(card_id=card_id)
    attachments = await client.list_attachments(card_id=card_id)
    return json.dumps(ensure_ascii=False, obj={
        "card": {
            "id": card.id,
            "name": card.name,
            "desc": card.description or "",
        },
        "checklists": [{"id": cl.id, "name": cl.name} for cl in checklists],
        "comments": [{"id": c.id, "text": c.text} for c in comments],
        "attachments": [{"id": a.id, "name": a.name, "url": a.url} for a in attachments],
    })
