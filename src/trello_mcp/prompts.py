from trello_mcp.server import server


@server.prompt(description="Generate a summary of a Trello board's current status.")
def summarize_board(board_id: str) -> str:
    return (
        f"Please summarize the current status of Trello board {board_id}. "
        f"Use the get_board_overview tool to fetch the board data, then "
        f"provide a concise summary of all lists and their cards."
    )


@server.prompt(description="Set up a new sprint on a Trello board.")
def create_sprint(board_id: str, sprint_name: str) -> str:
    return (
        f"Create a new sprint called '{sprint_name}' on Trello board {board_id}. "
        f"First use get_board_overview to see the current board state, then "
        f"create lists for the sprint phases (To Do, In Progress, Review, Done) "
        f"using the create_list tool."
    )


@server.prompt(description="Generate a daily standup report from a Trello board.")
def daily_standup(board_id: str) -> str:
    return (
        f"Generate a daily standup report for Trello board {board_id}. "
        f"Use the get_board_overview tool to fetch current board data, then "
        f"organize the information into: what was done, what is in progress, "
        f"and what is blocked."
    )


async def get_prompt_messages(name: str, arguments: dict) -> str:
    if name == "summarize_board":
        return summarize_board(board_id=arguments["board_id"])
    elif name == "create_sprint":
        return create_sprint(
            board_id=arguments["board_id"],
            sprint_name=arguments["sprint_name"],
        )
    elif name == "daily_standup":
        return daily_standup(board_id=arguments["board_id"])
    else:
        raise ValueError(f"Unknown prompt: {name}")
