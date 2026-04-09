import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        from trello_mcp.auth import auth_command
        auth_command()
    else:
        from trello_mcp import server
        server.run(transport="stdio")


if __name__ == "__main__":
    main()
