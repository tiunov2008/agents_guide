import json
import sys

from anthropic import beta_tool

from client import client


@beta_tool
def get_weather(location: str) -> str:
    """Get the weather for a given location.

    Args:
        location: The city and state, for example, San Francisco, CA
    Returns:
        A JSON-encoded string with the location, temperature, and weather condition.
    """
    return json.dumps(
        {
            "location": location,
            "temperature": "68°F",
            "condition": "Sunny",
        }
    )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # The tool runner automatically executes tool calls and returns each message.
    runner = client.beta.messages.tool_runner(
        max_tokens=1024,
        model="claude-opus-4-8",
        tools=[get_weather],
        messages=[
            {"role": "user", "content": "What is the weather in SF?"},
        ],
    )

    for message in runner:
        print(message)


if __name__ == "__main__":
    main()
