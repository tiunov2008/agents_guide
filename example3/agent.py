import sys

from anthropic import beta_tool

from client import client
from tools.math_tool import math_tool
from tools.math_tool import math_tool_desc


def run_math_tool(expression: str) -> str:
    return str(math_tool(expression))


registered_math_tool = beta_tool(
    name=math_tool_desc["name"],
    description=math_tool_desc["description"].strip(),
    input_schema=math_tool_desc["input_schema"],
)(run_math_tool)

tools = [registered_math_tool.to_dict()]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    message = client.messages.create(
        max_tokens=1024,
        model="claude-opus-4-8",
        tools=tools,
        tool_choice={"type": "tool", "name": registered_math_tool.name},
        messages=[
            {"role": "user", "content": input("Вы: ")},
        ],
    )

    for block in message.content:
        if block.type == "tool_use" and block.name == registered_math_tool.name:
            result = registered_math_tool.call(block.input)
            print(f"Результат: {result}")
            return

    raise RuntimeError("Модель не вызвала math_tool")


if __name__ == "__main__":
    main()
