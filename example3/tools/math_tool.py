from pathlib import Path
from math import *

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "math_tool.md"
MATH_TOOL_PROMPT = PROMPT_PATH.read_text(encoding="utf-8").strip()


def math_tool(exp: str) -> int:
    return eval(exp)


math_tool_desc = {
    "name": "math_tool",
    "description": MATH_TOOL_PROMPT,
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": (
                    "Математическое выражение для вычисления, "
                    "например: '(2 + 3) * 4'"
                ),
            }
        },
        "required": ["expression"],
        "additionalProperties": False,
    },
}
