from unittest.mock import AsyncMock
from trellio import TrellioClient
from trellio.models import TrelloList
from trello_mcp.server import set_client


def before_scenario(context, scenario):
    mock_client = AsyncMock(spec=TrellioClient)

    # Default: get_list returns an active (non-archived) list.
    # Scenarios that test archived list behavior override this.
    async def default_get_list(list_id, **kwargs):
        return TrelloList(id=list_id, name="Mock List", idBoard="bd-000", closed=False)
    mock_client.get_list.side_effect = default_get_list

    set_client(mock_client)
    context.mock_client = mock_client
    context.result = None
    context.error = None


def after_scenario(context, scenario):
    set_client(None)
