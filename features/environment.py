from unittest.mock import AsyncMock
from trellio import TrellioClient
from trello_mcp.server import set_client


def before_scenario(context, scenario):
    mock_client = AsyncMock(spec=TrellioClient)
    set_client(mock_client)
    context.mock_client = mock_client
    context.result = None
    context.error = None


def after_scenario(context, scenario):
    set_client(None)
