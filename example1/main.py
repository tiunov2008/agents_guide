import httpx
from anthropic import Anthropic

API_KEY = "sk-ant-JN6th9EjYLAmfyoinztZPmysCVORDd2bfjso1QcYNT1"

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


user_input = input()

message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": user_input,
        }
    ],
    model="claude-opus-4-8",
)

print(message.content)