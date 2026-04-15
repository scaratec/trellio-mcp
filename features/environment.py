from unittest.mock import AsyncMock
from trellio import TrellioClient
from trellio.models import TrelloBoard, TrelloList, TrelloCard
from trello_mcp.server import set_client


def before_scenario(context, scenario):
    mock_client = AsyncMock(spec=TrellioClient)

    # Defaults: all objects are active (non-archived).
    # Scenarios testing archived behavior override these.
    async def default_get_board(board_id, **kwargs):
        return TrelloBoard(id=board_id, name="Mock Board", closed=False)

    async def default_get_list(list_id, **kwargs):
        return TrelloList(id=list_id, name="Mock List", idBoard="bd-000", closed=False)

    async def default_get_card(card_id, **kwargs):
        return TrelloCard(id=card_id, name="Mock Card", idList="ls-000", closed=False)

    mock_client.get_board.side_effect = default_get_board
    mock_client.get_list.side_effect = default_get_list
    mock_client.get_card.side_effect = default_get_card

    set_client(mock_client)
    context.mock_client = mock_client
    context.result = None
    context.error = None


def after_scenario(context, scenario):
    set_client(None)
