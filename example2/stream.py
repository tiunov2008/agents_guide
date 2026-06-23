import sys

from client import client


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    with client.messages.stream(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Say hello there!",
            }
        ],
        model="claude-opus-4-8",
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        print()

        message = stream.get_final_message()
        print(message.to_json())


if __name__ == "__main__":
    main()
