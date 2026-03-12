"""
Minimal MVP tools.

Each tool is a simple Python function for early testing.
"""

from typing import Any


def echo_tool(message: str) -> dict:
    """
    Echoes the input message.
    """
    return {"echo": message}


def sum_tool(a: float, b: float) -> float:
    """
    Returns the sum of two numbers.
    """
    return a + b