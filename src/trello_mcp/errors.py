from mcp.server.fastmcp.exceptions import ToolError
from trellio import TrelloAPIError


def handle_api_error(e: TrelloAPIError) -> None:
    messages = {
        400: f"Invalid input: {e.message}",
        401: "Authentication failed. Check TRELLO_API_KEY and TRELLO_TOKEN.",
        403: f"Forbidden: {e.message}",
        404: "Not found. Use a list_* tool to find valid IDs.",
        429: f"Rate limited by Trello. {e.message}",
        0: "Request timed out.",
    }
    msg = messages.get(
        e.status_code,
        f"Trello error ({e.status_code}): {e.message}",
    )
    raise ToolError(msg)
