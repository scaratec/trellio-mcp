import json
import os
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional
from urllib.parse import urlencode


def _credentials_dir() -> str:
    return os.path.join(os.path.expanduser("~"), ".config", "trellio-mcp")


def _credentials_path() -> str:
    return os.path.join(_credentials_dir(), "credentials.json")


def load_credentials() -> Optional[tuple[str, str]]:
    path = _credentials_path()
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        data = json.load(f)
    api_key = data.get("api_key", "")
    token = data.get("token", "")
    if api_key and token:
        return api_key, token
    return None


def store_credentials(api_key: str, token: str) -> None:
    cred_dir = _credentials_dir()
    os.makedirs(cred_dir, mode=0o700, exist_ok=True)
    path = _credentials_path()
    with open(path, "w") as f:
        json.dump({"api_key": api_key, "token": token}, f, indent=2)
    os.chmod(path, 0o600)


def build_auth_url(api_key: str, port: int) -> str:
    params = {
        "key": api_key,
        "name": "trellio-mcp",
        "expiration": "never",
        "scope": "read,write",
        "response_type": "token",
        "callback_method": "fragment",
        "return_url": f"http://localhost:{port}/callback",
    }
    return f"https://trello.com/1/authorize?{urlencode(params)}"


CALLBACK_HTML = """<!DOCTYPE html>
<html>
<head><title>trellio-mcp Authorization</title></head>
<body>
<h2>Authorizing trellio-mcp...</h2>
<p id="status">Capturing token...</p>
<script>
const hash = window.location.hash;
const token = hash.replace('#token=', '');
if (token && token !== hash) {
    fetch('/capture', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({token: token})
    }).then(() => {
        document.getElementById('status').textContent =
            'Authorization successful! You can close this tab.';
    });
} else {
    document.getElementById('status').textContent =
        'Authorization denied or no token received.';
}
</script>
</body>
</html>"""

SUCCESS_HTML = """<!DOCTYPE html>
<html>
<head><title>trellio-mcp</title></head>
<body><h2>Token captured. You can close this tab.</h2></body>
</html>"""


def auth_command() -> None:
    api_key = os.environ.get("TRELLO_API_KEY", "")
    if not api_key:
        api_key = input("Enter your Trello API Key: ").strip()
    if not api_key:
        print("Error: API Key is required.")
        raise SystemExit(1)

    captured_token = None

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/callback"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(CALLBACK_HTML.encode())
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            nonlocal captured_token
            if self.path == "/capture":
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length))
                captured_token = body.get("token", "")
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(SUCCESS_HTML.encode())
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            pass

    port = 8095
    server = None
    for p in range(8095, 8100):
        try:
            server = HTTPServer(("localhost", p), CallbackHandler)
            port = p
            break
        except OSError:
            continue

    if server is None:
        print("Error: Could not bind to any port (8095-8099).")
        raise SystemExit(1)

    auth_url = build_auth_url(api_key, port)
    print(f"Opening browser for Trello authorization...")
    print(f"If the browser doesn't open, visit:\n{auth_url}\n")
    webbrowser.open(auth_url)

    print("Waiting for authorization...")
    while captured_token is None:
        server.handle_request()

    server.server_close()

    if captured_token:
        store_credentials(api_key, captured_token)
        print(f"\nAuthorization successful!")
        print(f"Credentials stored in {_credentials_path()}")
    else:
        print("\nAuthorization failed: no token received.")
        raise SystemExit(1)
