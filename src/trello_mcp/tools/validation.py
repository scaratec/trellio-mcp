from mcp.server.fastmcp.exceptions import ToolError


async def check_board_not_archived(client, board_id: str) -> None:
    board = await client.get_board(board_id=board_id)
    if board.closed:
        raise ToolError(
            f"Target board '{board.name}' ({board_id}) is archived. "
            f"Use an active board or unarchive it first."
        )


async def check_list_not_archived(client, list_id: str) -> None:
    trello_list = await client.get_list(list_id=list_id)
    if trello_list.closed:
        raise ToolError(
            f"Target list '{trello_list.name}' ({list_id}) is archived. "
            f"Use an active list or unarchive it first."
        )


async def check_card_not_archived(client, card_id: str) -> None:
    card = await client.get_card(card_id=card_id)
    if card.closed:
        raise ToolError(
            f"Target card '{card.name}' ({card_id}) is archived. "
            f"Use an active card or unarchive it first."
        )
