import os

import httpx
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not API_KEY:
    raise RuntimeError("ANTHROPIC_API_KEY is not set in example2/.env")

def clean_sdk_headers(request: httpx.Request) -> None:
    """Remove SDK metadata for compatible proxies that reject it."""
    for name in list(request.headers):
        if name.lower().startswith("x-stainless-"):
            del request.headers[name]
    request.headers["user-agent"] = "excel-code-agent/0.1"

http_client = httpx.Client(
    event_hooks={"request": [clean_sdk_headers]},
    timeout=60,
)

client = Anthropic(
    api_key=API_KEY,
    base_url="https://api.cheat-ai.shop",
    http_client=http_client,
)
