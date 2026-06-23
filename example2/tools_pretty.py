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


def print_pretty_message(message: object) -> None:
    """Print the useful parts of an Anthropic message in a readable form."""
    print("\n" + "─" * 60)
    print(f"Роль: {getattr(message, 'role', 'unknown')}")

    for block in getattr(message, "content", []):
        block_type = getattr(block, "type", "unknown")

        if block_type == "text":
            print(f"\nТекст:\n{block.text}")
        elif block_type == "tool_use":
            arguments = json.dumps(block.input, ensure_ascii=False, indent=2)
            print(f"\nВызов инструмента: {block.name}")
            print(f"Аргументы:\n{arguments}")
        elif block_type == "tool_result":
            print(f"\nРезультат инструмента:\n{block.content}")
        else:
            print(f"\nБлок {block_type}:\n{block}")

    stop_reason = getattr(message, "stop_reason", None)
    if stop_reason:
        print(f"\nПричина остановки: {stop_reason}")

    usage = getattr(message, "usage", None)
    if usage:
        print(
            "Токены: "
            f"вход — {usage.input_tokens}, "
            f"выход — {usage.output_tokens}"
        )
    print("─" * 60)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    runner = client.beta.messages.tool_runner(
        max_tokens=1024,
        model="claude-opus-4-8",
        tools=[get_weather],
        messages=[
            {"role": "user", "content": "What is the weather in SF?"},
        ],
    )

    for message in runner:
        print_pretty_message(message)


if __name__ == "__main__":
    main()
