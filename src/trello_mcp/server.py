import os
from mcp.server.fastmcp import FastMCP
from trellio import TrellioClient

server = FastMCP(name="trello-mcp")

_client: TrellioClient | None = None


def get_client() -> TrellioClient:
    global _client
    if _client is None:
        from trello_mcp.auth import load_credentials
        creds = load_credentials()
        if creds:
            api_key, token = creds
        else:
            api_key = os.environ["TRELLO_API_KEY"]
            token = os.environ["TRELLO_TOKEN"]
        _client = TrellioClient(api_key=api_key, token=token)
    return _client


def set_client(client) -> None:
    global _client
    _client = client
